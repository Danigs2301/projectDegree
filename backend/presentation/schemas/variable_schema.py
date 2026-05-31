from pydantic import BaseModel


class CreateVariableRequest(BaseModel):
    name: str
    unit: str


class VariableResponse(BaseModel):
    id: str
    name: str
    unit: str