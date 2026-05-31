from services.domain_services.change_alert import ChangeAlert
from data.repositories.alert_repository import AlertRepository
from data.repositories.model_repository import ModelRepository
from data.repositories.sample_repository import SampleRepository
from typing import Optional, List


class AlertService:

    def __init__(self):
        self.repository = AlertRepository()
        self.model_repository = ModelRepository()
        self.sample_repository = SampleRepository()

    def create_alert(
        self,
        sample_id: str,
        model_id: str,
        cluster_id: str,
        t2_statistic: float,
        control_limit: float
    ) -> ChangeAlert:
        model = self.model_repository.find_by_id(model_id)
        if model is None:
            raise ValueError(f"Modelo con id {model_id} no encontrado")

        sample = self.sample_repository.find_by_id(sample_id)
        if sample is None:
            raise ValueError(f"Muestra con id {sample_id} no encontrada")

        cluster_ids = [cp.cluster_id for cp in model.cluster_profiles]
        if cluster_id not in cluster_ids:
            raise ValueError(f"Cluster {cluster_id} no pertenece al modelo {model_id}")

        alert = ChangeAlert(
            sample_id=sample_id,
            model_id=model_id,
            cluster_id=cluster_id,
            t2_statistic=t2_statistic,
            control_limit=control_limit
        )
        return self.repository.save(alert)

    def get_alert(self, alert_id: str) -> Optional[ChangeAlert]:
        alert = self.repository.find_by_id(alert_id)
        if alert is None:
            raise ValueError(f"Alerta con id {alert_id} no encontrada")
        return alert

    def get_alerts_by_model(self, model_id: str) -> List[ChangeAlert]:
        model = self.model_repository.find_by_id(model_id)
        if model is None:
            raise ValueError(f"Modelo con id {model_id} no encontrado")
        return self.repository.find_by_model_id(model_id)

    def get_alerts_by_sample(self, sample_id: str) -> List[ChangeAlert]:
        sample = self.sample_repository.find_by_id(sample_id)
        if sample is None:
            raise ValueError(f"Muestra con id {sample_id} no encontrada")
        return self.repository.find_by_sample_id(sample_id)

    def confirm_alert(self, alert_id: str) -> ChangeAlert:
        alert = self.repository.find_by_id(alert_id)
        if alert is None:
            raise ValueError(f"Alerta con id {alert_id} no encontrada")
        if alert.confirmed:
            raise ValueError(f"La alerta {alert_id} ya está confirmada")
        self.repository.confirm(alert_id)
        return self.repository.find_by_id(alert_id)