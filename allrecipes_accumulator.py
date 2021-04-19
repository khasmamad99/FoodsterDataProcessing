"""
This file is getting too long and compilacted. Consider scraping in the same
way before Perman's edits and doing the edits with a different file.
"""


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
from scripts.scraping_pool import CustomScrapingPool

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
    seen_urls = set()

    urls_dict = srsly.read_json(urls_json_path)
    for cat, urls in urls_dict.items():
        for url in tqdm(urls[:recipe_count_per_cat]):
            if url in seen_urls:
                continue
            seen_urls.add(url)
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
    paranth_rgx = re.compile(r'[0-9]+ +\([^)]*\)')
    if ingredients:
        for ingredient in ingredients:
            ingredient = ascii_forcer(fraction_tamer(ingredient))

            # remove parantheses before processing
            doc = ner_model(ingredient)
            entity_list = list()
            seen = {
                "NAME" : 0,
                "QUANTITY" : 0,
                "UNIT" : 0
            }
            for ent in doc.ents:
                text = ent.text
                label = ent.label_
                start = ingredient.find(text)
                end = start + len(text)

                # count encounters of entities in seen
                if label in seen:
                    seen[label] += 1

                # convert fractions to decimal points
                if label == "QUANTITY":
                    text = replace_ratios(text)
                
                entity_list.append(Entity(
                    text=text,
                    label=label,
                    # start=start,
                    # end=end
                ))

            # make sure that there is exactly 1 NAME and at most 1 QUANTITY and UNIT
            print(ingredient)
            print(seen)
            print()
            if seen['QUANTITY'] > 2 or seen['UNIT'] > 2 or seen['NAME'] != 1:
                return None
            elif seen['UNIT'] == 2 and seen['QUANTITY'] == 2:
                """Handle the cases such as '2 (3 ounce) cans of tomatoes'
                   by multiplying the can number with can size to find the
                   total size and using the total size as the quantity and
                   the first unit (ounce) as the unit
                """
                # return None if the pattern like '2 (3 ounce)' is not in the text
                if not paranth_rgx.search(ingredient):
                    return None
                # extract the units and quantities
                units = [ent.text for ent in entity_list if ent.label == "UNIT"]
                quants = [ent.text for ent in entity_list if ent.label == "QUANTITY"]
                # merge the quants and use the first unit
                quant = float(quants[0]) * float(quants[1])
                unit = units[0]
                # remove old units and quantities add the new ones
                entity_list = [ent for ent in entity_list if ent.label != "UNIT" and ent.label != "QUANTITY"]
                entity_list.append(Entity(text=str(quant), label="QUANTITY"))
                entity_list.append(Entity(text=unit, label="UNIT"))
            elif seen["UNIT"] > 1 or seen["QUANTITY"] > 1:
                return None

            if not len(entity_list) > 0: entity_list = None
            ingredients_list.append(Ingredient(
                description=ingredient,
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
