from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CreateProcessRequest(BaseModel):
    name: str


class AssignVariableRequest(BaseModel):
    variable_id: str


class ProcessResponse(BaseModel):
    id: str
    name: str
    variable_ids: List[str]
    creation_date: datetime
    state: str