from pydantic import BaseModel
from datetime import datetime
from typing import List


class MeasurementRequest(BaseModel):
    variable_id: str
    value: float


class CreateSampleRequest(BaseModel):
    process_id: str
    measurements: List[MeasurementRequest]


class MeasurementResponse(BaseModel):
    measurement_id: str
    variable_id: str
    value: float


class SampleResponse(BaseModel):
    id: str
    process_id: str
    date: datetime
    measurements: List[MeasurementResponse]