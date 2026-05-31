from pydantic import BaseModel, Field
from bson import ObjectId

class Variable(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    unit: str

    class Config:
        populate_by_name = True