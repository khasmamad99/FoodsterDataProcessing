from multiprocessing.pool import ThreadPool as Pool
import uuid

from pathlib import Path
import srsly
import typer
import spacy
from tqdm import tqdm

from scrape.allrecipes import AllRecipes
from scripts.utils import *

from models.ingredient import Ingredient
from models.nutrient import Nutrients
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
    image_b64 = img_url2b64(image_url)

    nutrients = scraper.nutrients()
    if nutrients:
        nutrients = Nutrients(**nutrients)

    ingredients = scraper.ingredients()
    ingredients_list = []
    if ingredients:
        for ingredient in ingredients:
            ingredient = ascii_forcer(fraction_tamer(ingredient))
            doc = ner_model(ingredient)
            entity_list = list()
            for ent in doc.ents:
                text = ent.text
                label = ent.label_
                start = ingredient.find(text)
                end = start + len(text)
                entity_list.append(Entity(
                    text = text,
                    label = label,
                    start = start,
                    end = end
                ))
            ingredients_list.append(Ingredient(
                text = ingredient,
                entities = entity_list
            ))

    ingredients = ingredients_list if len(ingredients_list) > 0 else None

    instructions = scraper.instructions()
    if instructions:
        instructions = [ascii_forcer(instr) for instr in instructions]

    rating = scraper.rating()
    if rating:
        rating = Rating(**rating)

    
    return Recipe(
        id = str(uuid.uuid4()),
        title = title,
        siteName = scraper.site_name(),
        category = cat,
        imageUrl = image_url,
        imageB64 = image_b64,
        totalTime = scraper.total_time(),
        prepTime = scraper.prep_time(),
        cookTime = scraper.cook_time(),
        servingSize = scraper.yields(),
        ingredients = ingredients,
        nutrients = nutrients,
        instructions = instructions,
        rating = rating
    )   


if __name__ == "__main__":
    typer.run(accumulate)