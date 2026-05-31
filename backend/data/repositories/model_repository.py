from data.infrastructure.mongodb import get_db
from services.domain_services.model import Model
from typing import Optional, List


class ModelRepository:

    def __init__(self):
        self.collection = get_db()["models"]

    def save(self, model: Model) -> Model:
        doc = model.model_dump()
        doc["_id"] = doc.pop("id")
        self.collection.insert_one(doc)
        return model

    def find_by_id(self, model_id: str) -> Optional[Model]:
        doc = self.collection.find_one({"_id": model_id})
        if doc is None:
            return None
        doc["id"] = doc.pop("_id")
        return Model(**doc)

    def find_by_process_id(self, process_id: str) -> List[Model]:
        docs = self.collection.find({"process_id": process_id})
        result = []
        for doc in docs:
            doc["id"] = doc.pop("_id")
            result.append(Model(**doc))
        return result

    def update(self, model: Model) -> Model:
        doc = model.model_dump()
        doc_id = doc.pop("id")
        self.collection.update_one({"_id": doc_id}, {"$set": doc})
        return model

    def logic_delete(self, model_id: str) -> bool:
        result = self.collection.update_one(
            {"_id": model_id},
            {"$set": {"state": "inactive"}}
        )
        return result.modified_count > 0