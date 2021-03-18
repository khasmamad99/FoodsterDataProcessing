from pydantic import BaseModel

class Rating(BaseModel):
    value: float
    count: int