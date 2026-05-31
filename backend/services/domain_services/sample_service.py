from services.domain_services.sample import Sample
from services.domain_services.process_measurement import ProcessMeasurement
from data.repositories.sample_repository import SampleRepository
from data.repositories.process_repository import ProcessRepository
from data.repositories.variable_repository import VariableRepository
from typing import Optional, List


class SampleService:

    def __init__(self):
        self.repository = SampleRepository()
        self.process_repository = ProcessRepository()
        self.variable_repository = VariableRepository()

    def create_sample(self, process_id: str, measurements: List[dict]) -> Sample:
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
        return self.repository.save(sample)

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