from typing import Optional, List

from pydantic import BaseModel
from .entity import Entity

class Ingredient(BaseModel):
    description: str
    entities: Optional[List[Entity]] = None
