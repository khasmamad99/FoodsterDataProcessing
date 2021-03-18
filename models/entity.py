from pydantic import BaseModel

class Entity(BaseModel):
    text: str
    label: str
    start: int
    end: int