from data.infrastructure.mongodb import get_db
from services.domain_services.sample import Sample
from typing import Optional, List


class SampleRepository:

    def __init__(self):
        self.collection = get_db()["samples"]

    def save(self, sample: Sample) -> Sample:
        doc = sample.model_dump()
        doc["_id"] = doc.pop("id")
        self.collection.insert_one(doc)
        return sample

    def find_by_id(self, sample_id: str) -> Optional[Sample]:
        doc = self.collection.find_one({"_id": sample_id})
        if doc is None:
            return None
        doc["id"] = doc.pop("_id")
        return Sample(**doc)

    def find_by_process_id(self, process_id: str) -> List[Sample]:
        docs = self.collection.find({"process_id": process_id})
        result = []
        for doc in docs:
            doc["id"] = doc.pop("_id")
            result.append(Sample(**doc))
        return result

    def delete(self, sample_id: str) -> bool:
        result = self.collection.delete_one({"_id": sample_id})
        return result.deleted_count > 0