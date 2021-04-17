from typing import Optional, List

from pydantic import BaseModel
from .entity import Entity

class Ingredient(BaseModel):
    # text: str
    entities: Optional[List[Entity]] = None
