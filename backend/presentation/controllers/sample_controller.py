from flask import request, jsonify
from services.domain_services.sample_service import SampleService
from presentation.schemas.sample_schema import CreateSampleRequest
from pydantic import ValidationError

service = SampleService()


def create_sample():
    try:
        body = CreateSampleRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    try:
        result = service.create_sample(
            process_id=body.process_id,
            measurements=[m.model_dump() for m in body.measurements]
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    response = {
        "sample": result["sample"].model_dump(),
        "detection": result["detection"]
    }
    return jsonify(response), 201


def get_sample(sample_id: str):
    try:
        sample = service.get_sample(sample_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify(sample.model_dump()), 200


def get_samples_by_process(process_id: str):
    try:
        samples = service.get_samples_by_process(process_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify([s.model_dump() for s in samples]), 200


def delete_sample(sample_id: str):
    try:
        service.delete_sample(sample_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({"message": f"Muestra {sample_id} eliminada correctamente"}), 200