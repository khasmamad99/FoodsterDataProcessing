from typing import Optional, Any

from pydantic import BaseModel


class Content(BaseModel):
    quantity: Any
    unit: Optional[str]

class Nutrients(BaseModel):
    calories: Content = None
    proteinContent: Content = None
    carbohydrateContent: Content = None
    fatContent: Content = None
    fiberContent: Optional[Content] = None
    cholestrolContent: Optional[Content] = None
    saturatedFatContent: Optional[Content] = None
    sodiumContent: Optional[Content] = None
    sugarContent: Optional[Content] = None
    transFatContent: Optional[Content] = None
    unsaturatedFatContent: Optional[Content] = None

