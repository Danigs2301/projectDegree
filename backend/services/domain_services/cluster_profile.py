from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List

class ClusterProfile(BaseModel):
    cluster_id: str = Field(default_factory=lambda: str(ObjectId()))
    centroid: List[float]
    covariance_matrix: List[List[float]]
    t2_control_limit: float
    n_observations: int