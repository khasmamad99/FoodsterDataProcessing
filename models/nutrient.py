from typing import Optional, Any

from pydantic import BaseModel


class Content(BaseModel):
    quantity: Any
    unit: Optional[str]

class Nutrients(BaseModel):
    calories: Content
    protein: Content
    carbs: Content
    fat: Content
    fiber: Optional[Content] = None
    cholestrol: Optional[Content] = None
    saturatedFat: Optional[Content] = None
    sodium: Optional[Content] = None
    sugar: Optional[Content] = None
    transFat: Optional[Content] = None
    unsaturatedFat: Optional[Content] = None

