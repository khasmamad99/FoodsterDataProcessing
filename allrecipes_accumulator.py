from multiprocessing.pool import ThreadPool as Pool
import uuid
import re

from pathlib import Path
import srsly
import typer
import spacy
from tqdm import tqdm

from scrape.allrecipes import AllRecipes
from scripts.utils import *

from models.ingredient import Ingredient
from models.nutrient import Nutrients, Content
from models.rating import Rating
from models.recipe import Recipe
from models.entity import Entity

ner_model = None


def accumulate(
        urls_json_path: Path,
        output_json_path: Path,
        ner_model_path: Path,
        recipe_count_per_cat: int
):
    pool_size = 8
    pool = Pool(pool_size)

    global ner_model
    ner_model = spacy.load(ner_model_path)

    data = []

    urls_dict = srsly.read_json(urls_json_path)
    for cat, urls in urls_dict.items():
        for url in tqdm(urls[:recipe_count_per_cat]):
            result = pool.apply_async(scrape, (url, cat))
            return_val = result.get()
            if return_val:
                data.append(return_val.dict())

    srsly.write_json(output_json_path, data)
    print("Saved output to:", output_json_path)


def scrape(url, cat):
    global ner_model

    scraper = AllRecipes(url)
    title = scraper.title()
    if title:
        title = ascii_forcer(scraper.title())

    image_url = scraper.image_url()

    # try:
    #     image_b64 = img_url2b64(image_url)
    # except:
    #     image_b64 = None

    nutrients = scraper.nutrients()
    if nutrients:
        try:
            nutrients.pop('@type')
            nutrients.pop('servingSize')
        except:
            pass
        rgx = re.compile('(\d+(?:\.\d+)?) ([a-zA-Z]+)?')
        for key, item in nutrients.items():
            try:
                matches = rgx.findall(item)[0]
                quantity, unit = matches
                content = Content(unit=unit, quantity=quantity)
                nutrients[key] = content
            except:
                continue
        nutrients = Nutrients(**nutrients)

    ingredients = scraper.ingredients()
    ingredients_list = []
    if ingredients:
        for ingredient in ingredients:
            ingredient = ascii_forcer(fraction_tamer(ingredient))
            doc = ner_model(ingredient)
            entity_list = list()
            seen_name = False
            for ent in doc.ents:
                text = ent.text
                label = ent.label_
                start = ingredient.find(text)
                end = start + len(text)

                # make sure that the NAME entity is there
                if label == "NAME":
                    seen_name = True

                # convert fractions to decimal points
                if label == "QUANTITY":
                    text = replace_ratios(text)
                
                entity_list.append(Entity(
                    text=text,
                    label=label,
                    # start=start,
                    # end=end
                ))

            if not seen_name:
                return None

            if not len(entity_list) > 0: entity_list = None
            ingredients_list.append(Ingredient(
                # text=ingredient,
                entities=entity_list
            ))

    ingredients = ingredients_list if len(ingredients_list) > 0 else None

    instructions = scraper.instructions()
    if instructions:
        instructions = [ascii_forcer(instr) for instr in instructions]

    rating = scraper.rating()
    if rating:
        rating = Rating(**rating)

    tags = scraper.tags()
    if tags:
        tags = [ascii_forcer(tag) for tag in tags]

    cuisines = scraper.cuisines()
    if cuisines:
        cuisines = [ascii_forcer(c) for c in cuisines]

    prepTime, cookTime, servingSize = scraper.prep_time(), scraper.cook_time(), scraper.yields()

    # skip if anything is missing
    if None in [title, image_url, nutrients, ingredients, instructions, rating, prepTime, cookTime, servingSize]:
        return None

    return Recipe(
        # this fields are not going to be used anywhere
        # id=str(uuid.uuid4()),
        # url=url,
        name=title,
        # siteName=scraper.site_name(),
        category=cat,
        imageUrl=image_url,
        # imageB64=image_b64,
        # totalTime=scraper.total_time(),
        prepTime=scraper.prep_time(),
        cookTime=scraper.cook_time(),
        servingSize=scraper.yields(),
        ingredients=ingredients,
        nutrition=nutrients,
        instructions=instructions,
        rating=rating,
        tags=tags,
        cuisines=cuisines
    )


if __name__ == "__main__":
    typer.run(accumulate)
