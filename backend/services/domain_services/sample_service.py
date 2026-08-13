from services.domain_services.sample import Sample
from services.domain_services.process_measurement import ProcessMeasurement
from data.repositories.sample_repository import SampleRepository
from data.repositories.process_repository import ProcessRepository
from data.repositories.variable_repository import VariableRepository
from data.repositories.model_repository import ModelRepository
from data.repositories.alert_repository import AlertRepository
from services.domain_services.change_alert import ChangeAlert
from services.analytical_engine.preprocessing import DataPreprocessor
from services.analytical_engine.core import KMeansMahalanobisEngine
import numpy as np
from typing import Optional, List


class SampleService:

    def __init__(self):
        self.repository = SampleRepository()
        self.process_repository = ProcessRepository()
        self.variable_repository = VariableRepository()
        self.model_repository = ModelRepository()
        self.alert_repository = AlertRepository()
        self.engine = KMeansMahalanobisEngine()

    def create_sample(self, process_id: str, measurements: List[dict]) -> dict:
        process = self.process_repository.find_by_id(process_id)
        if process is None:
            raise ValueError(f"Proceso con id {process_id} no encontrado")
        if process.state == "inactive":
            raise ValueError("No se puede agregar muestras a un proceso inactivo")

        process_measurements = []
        for m in measurements:
            variable_id = m.get("variable_id")
            if variable_id not in process.variable_ids:
                raise ValueError(f"La variable {variable_id} no está asignada al proceso")
            variable = self.variable_repository.find_by_id(variable_id)
            if variable is None:
                raise ValueError(f"Variable con id {variable_id} no encontrada")
            process_measurements.append(
                ProcessMeasurement(variable_id=variable_id, value=m.get("value"))
            )

        sample = Sample(process_id=process_id, measurements=process_measurements)
        self.repository.save(sample)

        detection_result = self._auto_detect(sample)

        return {
            "sample": sample,
            "detection": detection_result
        }

    def _auto_detect(self, sample: Sample) -> Optional[dict]:
        models = self.model_repository.find_by_process_id(sample.process_id)
        active_models = [m for m in models if m.state == "trained"]

        if not active_models:
            return None

        model = active_models[-1]

        if not model.cluster_profiles:
            return None

        try:
            x = self._preprocess_sample(sample, model)
            cluster_id, t2, control_limit, is_anomaly = self.engine.detect_change(
                x, model.cluster_profiles
            )

            result = {
                "sample_id": sample.id,
                "model_id": model.id,
                "cluster_id": cluster_id,
                "t2_statistic": round(t2, 6),
                "control_limit": round(control_limit, 6),
                "is_anomaly": is_anomaly,
                "alert_id": None
            }

            if is_anomaly:
                alert = ChangeAlert(
                    sample_id=sample.id,
                    model_id=model.id,
                    cluster_id=cluster_id,
                    t2_statistic=t2,
                    control_limit=control_limit
                )
                saved_alert = self.alert_repository.save(alert)
                result["alert_id"] = saved_alert.id

            return result

        except Exception as e:
            print(f"Error en detección automática: {e}")
            return None

    def _preprocess_sample(self, sample: Sample, model) -> np.ndarray:
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

    def get_sample(self, sample_id: str) -> Optional[Sample]:
        sample = self.repository.find_by_id(sample_id)
        if sample is None:
            raise ValueError(f"Muestra con id {sample_id} no encontrada")
        return sample

    def get_samples_by_process(self, process_id: str) -> List[Sample]:
        process = self.process_repository.find_by_id(process_id)
        if process is None:
            raise ValueError(f"Proceso con id {process_id} no encontrado")
        return self.repository.find_by_process_id(process_id)

    def delete_sample(self, sample_id: str) -> None:
        sample = self.repository.find_by_id(sample_id)
        if sample is None:
            raise ValueError(f"Muestra con id {sample_id} no encontrada")
        self.repository.delete(sample_id)