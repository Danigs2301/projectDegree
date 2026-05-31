from pydantic import BaseModel, Field
from bson import ObjectId

class ProcessMeasurement(BaseModel):
    measurement_id: str = Field(default_factory=lambda: str(ObjectId()))
    variable_id: str
    value: float