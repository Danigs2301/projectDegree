from flask import request, jsonify
from services.domain_services.variable_service import VariableService
from presentation.schemas.variable_schema import CreateVariableRequest
from pydantic import ValidationError

service = VariableService()


def create_variable():
    try:
        body = CreateVariableRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    variable = service.create_variable(name=body.name, unit=body.unit)
    return jsonify(variable.model_dump()), 201


def get_variable(variable_id: str):
    try:
        variable = service.get_variable(variable_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify(variable.model_dump()), 200


def get_all_variables():
    variables = service.get_all_variables()
    return jsonify([v.model_dump() for v in variables]), 200


def delete_variable(variable_id: str):
    try:
        service.delete_variable(variable_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({"message": f"Variable {variable_id} eliminada correctamente"}), 200