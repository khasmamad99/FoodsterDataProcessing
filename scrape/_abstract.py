from typing import Optional, Dict, Any, List

import requests
from bs4 import BeautifulSoup


class AbstractScraper:

    def __init__(self, url):
        page_data = requests.get(url).content
        self.soup = BeautifulSoup(page_data, "html_parser")
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

    def image_b64(self) -> Optional[str]:
        raise NotImplementedError("This should be implemented.")

    def nutrients(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("This should be implemented.")

    def ingredients(self) -> Optional[List[str]]:
        raise NotImplementedError("This should be implemented.")

    def instructions(self) -> Optional[List[str]]:
        raise NotImplementedError("This should be implemented.")
        
    def rating(self) -> Optional[float]:
        raise NotImplementedError("This should be implemented.")

    def site_name(self) -> Optional[str]:
        meta = self.soup.find("meta", property="og:site_name")
        return meta.get('content') if meta else None

    
