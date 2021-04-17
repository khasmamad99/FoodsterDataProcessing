from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from .ingredient import Ingredient
from .nutrient import Nutrients
from .rating import Rating


class Recipe(BaseModel):
    # id: Optional[str]
    # url: Optional[str]
    name: Optional[str]
    # siteName:Optional[str]
    category: Optional[str]
    imageUrl: Optional[str]
    # imageB64: Optional[str]
    # totalTime: Optional[int]
    prepTime: Optional[int]
    cookTime: Optional[int]
    servingSize: Optional[float]
    ingredients: Optional[List[Ingredient]]
    nutrition: Optional[Nutrients]
    instructions: Optional[List[str]]
    rating: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    cuisines: Optional[List[str]]

