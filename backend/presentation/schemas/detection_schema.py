from pydantic import BaseModel
from typing import Optional


class DetectionRequest(BaseModel):
    model_id: str
    sample_id: str


class DetectionResponse(BaseModel):
    sample_id: str
    model_id: str
    cluster_id: str
    t2_statistic: float
    control_limit: float
    is_anomaly: bool
    alert_id: Optional[str]