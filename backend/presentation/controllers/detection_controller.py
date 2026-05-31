from flask import request, jsonify
from services.domain_services.detection_service import DetectionService
from presentation.schemas.detection_schema import DetectionRequest
from pydantic import ValidationError

service = DetectionService()


def detect():
    try:
        body = DetectionRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    try:
        result = service.detect(
            model_id=body.model_id,
            sample_id=body.sample_id
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(result), 200