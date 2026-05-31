from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any


class CreateModelRequest(BaseModel):
    name: str
    type_model: str
    process_id: str


class ClusterProfileResponse(BaseModel):
    cluster_id: str
    centroid: List[float]
    t2_control_limit: float
    n_observations: int


class ModelResponse(BaseModel):
    id: str
    name: str
    type_model: str
    training_date: datetime
    process_id: str
    accuracy: float
    state: str
    parameters: Dict[str, Any]
    cluster_profiles: List[ClusterProfileResponse]