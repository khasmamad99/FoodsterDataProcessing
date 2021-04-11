# FoodsterDataProcessing

### Scraping AllRecipes

1. **Gather recipe URLs**. This process is facilitated with the script  `scripts/allrecipes_urls.py`. This script is executed with the following command: python allrecipes_urls.py INPUT_PATH OUTPUT_PATH URL_PER_CAT.
- INPUT_PATH: path to the json file that contains recipe categories and their corresponding URL pieces. For example, all the  breakfast and brunch recipes are collected under https://www.allrecipes.com/recipes/78/breakfast-and-brunch/. So, an entry in the input json file can be of the form `"breakfast_and_brunch" : "78/breakfast-and-brunch/"`.
- OUTPUT_PATH: this is where the output json file is going to be saved. The format of the output is `"category_name" : List of full recipe urls under this category.`
- URLS_PER_CAT: this parameter dictates the number of URLs to be collected per category.

2. **Scrape the URLs**. This is done with the script named `allrecipes_accumulator.py`. This script is executed with the following command: python allrecipes_accumulator.py URLS_JSON_PATH OUTPUT_JSON_PATH NER_MODEL_PATH RECIPE_COUNT_PER_CAT
- URLS_JSON_PATH: path to the json file outputted from `allrecipes_urls.py`.
- OUTPUT_JSON_PATH: this is where the output json file is going to be saved. The format of the output is given [here](https://drive.google.com/file/d/1B1gc33zUYqENnkEFBkMIKwzT_e3Dpcl1/view?usp=sharing).
- NER_MODEL_PATH: path to the NER model (the model is not uploaded to repo, due to its large size).
- URLS_PER_CAT: this parameter dictates the number of URLs to be scraped per category. The total number of recipes is expected to be equal to NUMBER_OF_CATEGORIES * URLS_PER_CAT.
