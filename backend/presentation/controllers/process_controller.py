from flask import request, jsonify
from services.domain_services.process_service import ProcessService
from presentation.schemas.process_schema import CreateProcessRequest, AssignVariableRequest
from pydantic import ValidationError

service = ProcessService()


def create_process():
    try:
        body = CreateProcessRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    process = service.create_process(name=body.name)
    return jsonify(process.model_dump()), 201


def get_process(process_id: str):
    try:
        process = service.get_process(process_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify(process.model_dump()), 200


def get_all_processes():
    processes = service.get_all_processes()
    return jsonify([p.model_dump() for p in processes]), 200


def delete_process(process_id: str):
    try:
        service.delete_process(process_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": f"Proceso {process_id} eliminado correctamente"}), 200


def assign_variable(process_id: str):
    try:
        body = AssignVariableRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    try:
        process = service.assign_variable(process_id, body.variable_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(process.model_dump()), 200