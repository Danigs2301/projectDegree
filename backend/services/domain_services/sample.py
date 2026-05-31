from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from typing import List
from services.domain_services.process_measurement import ProcessMeasurement

class Sample(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    process_id: str
    date: datetime = Field(default_factory=datetime.utcnow)
    measurements: List[ProcessMeasurement] = []