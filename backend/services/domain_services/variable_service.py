from services.domain_services.variable import Variable
from data.repositories.variable_repository import VariableRepository
from typing import Optional, List


class VariableService:

    def __init__(self):
        self.repository = VariableRepository()

    def create_variable(self, name: str, unit: str) -> Variable:
        variable = Variable(name=name, unit=unit)
        return self.repository.save(variable)

    def get_variable(self, variable_id: str) -> Optional[Variable]:
        variable = self.repository.find_by_id(variable_id)
        if variable is None:
            raise ValueError(f"Variable con id {variable_id} no encontrada")
        return variable

    def get_all_variables(self) -> List[Variable]:
        return self.repository.find_all()

    def delete_variable(self, variable_id: str) -> None:
        variable = self.repository.find_by_id(variable_id)
        if variable is None:
            raise ValueError(f"Variable con id {variable_id} no encontrada")
        self.repository.delete(variable_id)