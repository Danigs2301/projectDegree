from services.domain_services.model import Model
from data.repositories.model_repository import ModelRepository
from data.repositories.process_repository import ProcessRepository
from data.repositories.sample_repository import SampleRepository
from services.analytical_engine.preprocessing import DataPreprocessor
from services.analytical_engine.core import KMeansMahalanobisEngine
from typing import Optional, List


class ModelService:

    def __init__(self):
        self.repository = ModelRepository()
        self.process_repository = ProcessRepository()
        self.sample_repository = SampleRepository()

    def create_model(self, name: str, type_model: str, process_id: str) -> Model:
        process = self.process_repository.find_by_id(process_id)
        if process is None:
            raise ValueError(f"Proceso con id {process_id} no encontrado")
        if process.state == "inactive":
            raise ValueError("No se puede crear un modelo para un proceso inactivo")
        if len(process.variable_ids) == 0:
            raise ValueError("El proceso no tiene variables asignadas")

        model = Model(name=name, type_model=type_model, process_id=process_id)
        return self.repository.save(model)

    def get_model(self, model_id: str) -> Optional[Model]:
        model = self.repository.find_by_id(model_id)
        if model is None:
            raise ValueError(f"Modelo con id {model_id} no encontrado")
        return model

    def get_models_by_process(self, process_id: str) -> List[Model]:
        process = self.process_repository.find_by_id(process_id)
        if process is None:
            raise ValueError(f"Proceso con id {process_id} no encontrado")
        return self.repository.find_by_process_id(process_id)

    def delete_model(self, model_id: str) -> None:
        model = self.repository.find_by_id(model_id)
        if model is None:
            raise ValueError(f"Modelo con id {model_id} no encontrado")
        if model.state == "inactive":
            raise ValueError(f"El modelo {model_id} ya está inactivo")
        self.repository.logic_delete(model_id)

    def get_samples_for_training(self, process_id: str) -> List[dict]:
        process = self.process_repository.find_by_id(process_id)
        if process is None:
            raise ValueError(f"Proceso con id {process_id} no encontrado")

        samples = self.sample_repository.find_by_process_id(process_id)
        if len(samples) == 0:
            raise ValueError("El proceso no tiene muestras para entrenar")

        result = []
        for sample in samples:
            row = {"sample_id": sample.id}
            for m in sample.measurements:
                row[m.variable_id] = m.value
            result.append(row)
        return result

    def train_model(self, model_id: str) -> Model:
        model = self.repository.find_by_id(model_id)
        if model is None:
            raise ValueError(f"Modelo con id {model_id} no encontrado")
        if model.state == "inactive":
            raise ValueError("No se puede entrenar un modelo inactivo")

        samples = self.get_samples_for_training(model.process_id)
        if len(samples) < 2:
            raise ValueError("Se necesitan al menos 2 muestras para entrenar")

        preprocessor = DataPreprocessor()
        X = preprocessor.fit_transform(samples)

        engine = KMeansMahalanobisEngine()
        cluster_profiles, accuracy, optimal_k = engine.train(X)

        model.cluster_profiles = cluster_profiles
        model.accuracy = accuracy
        model.parameters = {
            "n_clusters": optimal_k,
            "scaler_mean": preprocessor.scaler.mean_.tolist(),
            "scaler_scale": preprocessor.scaler.scale_.tolist(),
            "variable_ids": preprocessor.get_variable_ids()
        }
        model.state = "trained"

        return self.repository.update(model)