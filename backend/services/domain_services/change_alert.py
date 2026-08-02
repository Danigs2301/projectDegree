from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime

class ChangeAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    sample_id: str
    model_id: str
    cluster_id: str
    detection_date: datetime = Field(default_factory=datetime.utcnow)
    t2_statistic: float
    control_limit: float
    confirmed: bool = False
    