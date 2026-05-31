from flask import request, jsonify
from services.domain_services.model_service import ModelService
from presentation.schemas.model_schema import CreateModelRequest
from pydantic import ValidationError

service = ModelService()


def create_model():
    try:
        body = CreateModelRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    try:
        model = service.create_model(
            name=body.name,
            type_model=body.type_model,
            process_id=body.process_id
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(model.model_dump()), 201


def get_model(model_id: str):
    try:
        model = service.get_model(model_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify(model.model_dump()), 200


def get_models_by_process(process_id: str):
    try:
        models = service.get_models_by_process(process_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify([m.model_dump() for m in models]), 200


def delete_model(model_id: str):
    try:
        service.delete_model(model_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": f"Modelo {model_id} eliminado correctamente"}), 200


def get_training_data(process_id: str):
    try:
        data = service.get_samples_for_training(process_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(data), 200

def train_model(model_id: str):
    try:
        model = service.train_model(model_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(model.model_dump()), 200