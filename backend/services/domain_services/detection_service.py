import numpy as np
from sklearn.preprocessing import StandardScaler
from services.domain_services.change_alert import ChangeAlert
from data.repositories.model_repository import ModelRepository
from data.repositories.sample_repository import SampleRepository
from data.repositories.alert_repository import AlertRepository
from services.analytical_engine.core import KMeansMahalanobisEngine


class DetectionService:

    def __init__(self):
        self.model_repository = ModelRepository()
        self.sample_repository = SampleRepository()
        self.alert_repository = AlertRepository()
        self.engine = KMeansMahalanobisEngine()

    def detect(self, model_id: str, sample_id: str) -> dict:
        model = self.model_repository.find_by_id(model_id)
        if model is None:
            raise ValueError(f"Modelo con id {model_id} no encontrado")
        if model.state == "inactive":
            raise ValueError("El modelo está inactivo")
        if not model.cluster_profiles:
            raise ValueError("El modelo no ha sido entrenado aún")

        sample = self.sample_repository.find_by_id(sample_id)
        if sample is None:
            raise ValueError(f"Muestra con id {sample_id} no encontrada")
        if sample.process_id != model.process_id:
            raise ValueError("La muestra no pertenece al proceso del modelo")

        x = self._preprocess_sample(sample, model)

        cluster_id, t2, control_limit, is_anomaly = self.engine.detect_change(
            x, model.cluster_profiles
        )

        result = {
            "sample_id": sample_id,
            "model_id": model_id,
            "cluster_id": cluster_id,
            "t2_statistic": round(t2, 6),
            "control_limit": round(control_limit, 6),
            "is_anomaly": is_anomaly,
            "alert_id": None
        }

        if is_anomaly:
            alert = ChangeAlert(
                sample_id=sample_id,
                model_id=model_id,
                cluster_id=cluster_id,
                t2_statistic=t2,
                control_limit=control_limit
            )
            saved_alert = self.alert_repository.save(alert)
            result["alert_id"] = saved_alert.id

        return result

    def _preprocess_sample(self, sample, model) -> np.ndarray:
        variable_ids = model.parameters.get("variable_ids", [])
        scaler_mean = model.parameters.get("scaler_mean", [])
        scaler_scale = model.parameters.get("scaler_scale", [])

        measurements = {m.variable_id: m.value for m in sample.measurements}

        row = []
        for var_id in variable_ids:
            if var_id not in measurements:
                raise ValueError(f"La muestra no tiene la variable {var_id}")
            row.append(measurements[var_id])

        x = np.array(row, dtype=float)

        mean = np.array(scaler_mean)
        scale = np.array(scaler_scale)
        x = (x - mean) / scale
        
        if model.parameters.get("use_pca"):
            pca_components = np.array(model.parameters.get("pca_components", []))
            pca_mean = np.array(model.parameters.get("pca_mean", []))
            x = (x - pca_mean) @ pca_components.T
        
        return x