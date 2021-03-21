from pathlib import Path
import srsly
import typer

import requests
import warnings
import re
from bs4 import BeautifulSoup



def generate_urls(
    input_path: Path, 
    output_path: Path, 
    url_per_cat: int
):

    source = "https://www.allrecipes.com"
    cat2type = srsly.read_json(input_path)
    output = dict()
    for cat_url, cat in cat2type.items():
        url_base = source + '/recipes/' + cat_url.strip('/')
        count_errors = 0
        page_no = 2
        output[cat] = []
        while count_errors < 3 and len(output[cat]) < url_per_cat:
            url = url_base + '/?page={}'.format(page_no)
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                page_no += 1
                soup = BeautifulSoup(r.content, 'html5lib')
                links = soup.find_all('a', {'class' : 'tout__titleLink'})
                for link in links:
                    link = link['href'][1:]
                    if link.startswith('recipe'):
                        full_link = source + "/" + link
                        output[cat].append(full_link)
                        if len(output[cat]) >= url_per_cat:
                            break
            else:
                count_errors += 1
                msg = f"Error no {count_errors} for {cat} with error code: {r.status_code}"
                warnings.warn(msg)
    
    print("Gathered:")
    for key, item in output.items():
        print(f"{key} : {len(item)} links")

    srsly.write_json(output_path, output)
    print("Output saved to:", output_path)



if __name__ == "__main__":
    typer.run(generate_urls)