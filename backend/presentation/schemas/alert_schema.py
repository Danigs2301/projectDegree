from pydantic import BaseModel
from datetime import datetime


class CreateAlertRequest(BaseModel):
    sample_id: str
    model_id: str
    cluster_id: str
    t2_statistic: float
    control_limit: float


class AlertResponse(BaseModel):
    id: str
    sample_id: str
    model_id: str
    cluster_id: str
    detection_date: datetime
    t2_statistic: float
    control_limit: float
    confirmed: bool