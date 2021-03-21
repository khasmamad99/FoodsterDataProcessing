from typing import Optional, Dict, Any, List

import requests
from bs4 import BeautifulSoup
import extruct


class AbstractScraper:

    def __init__(self, url):
        page_data = requests.get(url).content
        try:
            self.schema = extruct.extract(page_data)['json-ld'][1]
        except:
            self.schema = None
        self.soup = BeautifulSoup(page_data, "html5lib")
        self.url = url

    def title(self) -> Optional[str]:
        raise NotImplementedError("This should be implemented.")

    def total_time(self) -> Optional[int]:
        """ total time it takes to prepare the recipe in minutes """
        raise NotImplementedError("This should be implemented.")

    def prep_time(self) -> Optional[int]:
        """ preparation time in minutes """
        raise NotImplementedError("This should be implemented.")

    def cook_time(self) -> Optional[int]:
        """ cooking time in minutes """
        raise NotImplementedError("This should be implemented.")

    def yields(self) -> Optional[float]:
        """ The number of servings or items in the recipe """
        raise NotImplementedError("This should be implemented.")

    def image_url(self) -> Optional[str]:
        raise NotImplementedError("This should be implemented.")

    def nutrients(self) -> Optional[Dict[str, str]]:
        raise NotImplementedError("This should be implemented.")

    def ingredients(self) -> Optional[List[str]]:
        raise NotImplementedError("This should be implemented.")

    def instructions(self) -> Optional[List[str]]:
        raise NotImplementedError("This should be implemented.")
        
    def rating(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("This should be implemented.")

    def tags(self) -> Optional[List[str]]:
        raise NotImplementedError("This should be implemented.")

    def cuisines(self) -> Optional[List[str]]:
        raise NotImplementedError("This should be implemented.")

    def site_name(self) -> Optional[str]:
        meta = self.soup.find("meta", property="og:site_name")
        return meta.get('content') if meta else None
    
