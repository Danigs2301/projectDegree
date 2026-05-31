from data.infrastructure.mongodb import get_db
from services.domain_services.change_alert import ChangeAlert
from typing import Optional, List


class AlertRepository:

    def __init__(self):
        self.collection = get_db()["change_alerts"]

    def save(self, alert: ChangeAlert) -> ChangeAlert:
        doc = alert.model_dump()
        doc["_id"] = doc.pop("id")
        self.collection.insert_one(doc)
        return alert

    def find_by_id(self, alert_id: str) -> Optional[ChangeAlert]:
        doc = self.collection.find_one({"_id": alert_id})
        if doc is None:
            return None
        doc["id"] = doc.pop("_id")
        return ChangeAlert(**doc)

    def find_by_model_id(self, model_id: str) -> List[ChangeAlert]:
        docs = self.collection.find({"model_id": model_id})
        result = []
        for doc in docs:
            doc["id"] = doc.pop("_id")
            result.append(ChangeAlert(**doc))
        return result

    def find_by_sample_id(self, sample_id: str) -> List[ChangeAlert]:
        docs = self.collection.find({"sample_id": sample_id})
        result = []
        for doc in docs:
            doc["id"] = doc.pop("_id")
            result.append(ChangeAlert(**doc))
        return result

    def confirm(self, alert_id: str) -> bool:
        result = self.collection.update_one(
            {"_id": alert_id},
            {"$set": {"confirmed": True}}
        )
        return result.modified_count > 0