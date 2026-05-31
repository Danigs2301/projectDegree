from bson import ObjectId
from data.infrastructure.mongodb import get_db
from services.domain_services.process import Process
from typing import Optional, List


class ProcessRepository:

    def __init__(self):
        self.collection = get_db()["processes"]

    def save(self, process: Process) -> Process:
        doc = process.model_dump()
        doc["_id"] = doc.pop("id")
        self.collection.insert_one(doc)
        return process

    def find_by_id(self, process_id: str) -> Optional[Process]:
        doc = self.collection.find_one({"_id": process_id})
        if doc is None:
            return None
        doc["id"] = doc.pop("_id")
        return Process(**doc)

    def find_all(self) -> List[Process]:
        docs = self.collection.find()
        result = []
        for doc in docs:
            doc["id"] = doc.pop("_id")
            result.append(Process(**doc))
        return result

    def update(self, process: Process) -> Process:
        doc = process.model_dump()
        doc_id = doc.pop("id")
        self.collection.update_one({"_id": doc_id}, {"$set": doc})
        return process

    def logic_delete(self, process_id: str) -> bool:
        result = self.collection.update_one(
            {"_id": process_id},
            {"$set": {"state": "inactive"}}
        )
        return result.modified_count > 0

    def assign_variable(self, process_id: str, variable_id: str) -> bool:
        result = self.collection.update_one(
            {"_id": process_id},
            {"$addToSet": {"variable_ids": variable_id}}
        )
        return result.modified_count > 0