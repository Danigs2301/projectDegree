from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Any
from services.domain_services.cluster_profile import ClusterProfile

class Model(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    type_model: str
    training_date: datetime = Field(default_factory=datetime.utcnow)
    process_id: str
    accuracy: float = 0.0
    state: str = "trained"
    parameters: Dict[str, Any] = {}
    cluster_profiles: List[ClusterProfile] = []