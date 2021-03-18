from typing import Optional

import re

from ._abstract import AbstractScraper
from ._utils import to_mins


class AllRecipes(AbstractScraper):

    def title(self):
        title = self.soup.find('h1', {'class' : 'headline heading-content'})
        return title.text if title else None

    def total_time(self):
        return self._time('total')

    def prep_time(self):
        return self._time('prep')

    def cook_time(self):
        return self._time('cook')

    def yields(self):
        try:
            container = self.soup.find(
                'section', {'class' : 'recipe-meta-container two-subcol-content clearfix'}
            )

            yields_container = container.find(
                text=re.compile('serving', re.IGNORECASE)
            ).parent.parent

            yields = yields_container.find(
                'div', {'class' : 'recipe-meta-item-body'}).text.strip()

            return float(yields)

        except:
            return None


    def image_url(self):
        try:
            container = self.soup.find('div', {'class' : 'image-container'})
            img_url = container.find('div', {'data-tracking-zone' : 'image'})['data-src']
            return img_url
        except:
            return None


    def nutrients(self):
        try:
            container = self.soup.find(
                'div', {'class' : 'partial recipe-nutrition-section'}
            ).find('div', {'class' : 'section-body'})

            nutrients = container.text.replace('Full Nutrition', '') \
                                 .strip()[:-1].split(';')[:4]

            nutr_dict = dict()
            rgx = re.compile('(\d+(?:\.\d+)?)([a-zA-Z]+)?')
            for i, nutr_name in enumerate(['calories', 'protein', 'carbs', 'fat']):
                content = dict()
                content['unit'] = None
                matches = rgx.findall(nutrients[i])[0]
                if len(matches) > 1:
                    quantity, unit = matches
                    content['unit'] = unit
                else:
                    quantity = matches[0]
                content['quantity'] = quantity
                nutr_dict[nutr_name] = content

            return nutr_dict

        except:
            return None


    def ingredients(self):
        container = self.soup.find_all('span', {'class' : 'ingredients-item-name'})
        if container is None:
            return None
        
        ingredients = list()
        for elmnt in container:
                ingredients.append(elmnt.text.strip())

        return ingredients if len(ingredients) > 0 else None


    def instructions(self):
        container = self.soup.find_all(
            'li', {'class' : 'subcontainer instructions-section-item'}
        )
        if container is None:
            return None
        
        instructions = list()
        for elmnt in container:
            phrase = elmnt.find('p')
            if phrase:
                instructions.append(phrase.text.strip())
            
        return instructions if len(instructions) > 0 else None


    def rating(self):
        try:
            container = self.soup.find('ul', {'class' : 'rating_list'})
            ratings = [0, 0, 0, 0, 0]
            rating_elmnts = self.soup.find_all('li', {'class' : 'rating'})
            number_rgx = re.compile(r'\d+\.*d*')
            for elmnt in rating_elmnts:
                idx = elmnt.find('span', {'class' : 'rating-stars'}).text.strip()
                idx = int(number_rgx.search(idx).group(0))
                count = elmnt.find('span', {'class' : 'rating-count'}).text.strip()
                count = int(number_rgx.search(count).group(0))
                ratings[idx-1] = count

            sum = 0
            total_count = 0
            for i, count in enumerate(ratings):
                sum += (i+1) * count
                total_count += count

            rating = dict()
            rating['value'] = float(sum / total_count) if total_count > 0 else 0
            rating['count'] = total_count
            return rating

        except:
            return None

           
    def _time(self, kind: str) -> Optional[int]:
        try:
            container = self.soup.find(
                'section', {'class' : 'recipe-meta-container two-subcol-content clearfix'}
            )

            time_container = container.find(
                text=re.compile(kind, re.IGNORECASE)
            ).parent.parent

            time = time_container.find(
                'div', {'class' : 'recipe-meta-item-body'}
            ).text.strip()

            return to_mins(time)

        except:
            return None

            