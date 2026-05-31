from data.infrastructure.mongodb import get_db
from services.domain_services.variable import Variable
from typing import Optional, List


class VariableRepository:

    def __init__(self):
        self.collection = get_db()["variables"]

    def save(self, variable: Variable) -> Variable:
        doc = variable.model_dump()
        doc["_id"] = doc.pop("id")
        self.collection.insert_one(doc)
        return variable

    def find_by_id(self, variable_id: str) -> Optional[Variable]:
        doc = self.collection.find_one({"_id": variable_id})
        if doc is None:
            return None
        doc["id"] = doc.pop("_id")
        return Variable(**doc)

    def find_all(self) -> List[Variable]:
        docs = self.collection.find()
        result = []
        for doc in docs:
            doc["id"] = doc.pop("_id")
            result.append(Variable(**doc))
        return result

    def delete(self, variable_id: str) -> bool:
        result = self.collection.delete_one({"_id": variable_id})
        return result.deleted_count > 0