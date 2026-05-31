from services.domain_services.process import Process
from data.repositories.process_repository import ProcessRepository
from typing import Optional, List


class ProcessService:

    def __init__(self):
        self.repository = ProcessRepository()

    def create_process(self, name: str) -> Process:
        process = Process(name=name)
        return self.repository.save(process)

    def get_process(self, process_id: str) -> Optional[Process]:
        process = self.repository.find_by_id(process_id)
        if process is None:
            raise ValueError(f"Proceso con id {process_id} no encontrado")
        return process

    def get_all_processes(self) -> List[Process]:
        return self.repository.find_all()

    def delete_process(self, process_id: str) -> None:
        process = self.repository.find_by_id(process_id)
        if process is None:
            raise ValueError(f"Proceso con id {process_id} no encontrado")
        if process.state == "inactive":
            raise ValueError(f"El proceso {process_id} ya está inactivo")
        self.repository.logic_delete(process_id)

    def assign_variable(self, process_id: str, variable_id: str) -> Process:
        process = self.repository.find_by_id(process_id)
        if process is None:
            raise ValueError(f"Proceso con id {process_id} no encontrado")
        if process.state == "inactive":
            raise ValueError("No se puede modificar un proceso inactivo")
        if variable_id in process.variable_ids:
            raise ValueError(f"La variable {variable_id} ya está asignada al proceso")
        self.repository.assign_variable(process_id, variable_id)
        return self.repository.find_by_id(process_id)