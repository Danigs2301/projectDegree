from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from typing import List

class Process(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    variable_ids: List[str] = []
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    state: str = "active"