from flask import request, jsonify
from services.domain_services.alert_service import AlertService
from presentation.schemas.alert_schema import CreateAlertRequest
from pydantic import ValidationError

service = AlertService()


def create_alert():
    try:
        body = CreateAlertRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    try:
        alert = service.create_alert(
            sample_id=body.sample_id,
            model_id=body.model_id,
            cluster_id=body.cluster_id,
            t2_statistic=body.t2_statistic,
            control_limit=body.control_limit
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(alert.model_dump()), 201


def get_alert(alert_id: str):
    try:
        alert = service.get_alert(alert_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify(alert.model_dump()), 200


def get_alerts_by_model(model_id: str):
    try:
        alerts = service.get_alerts_by_model(model_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify([a.model_dump() for a in alerts]), 200


def get_alerts_by_sample(sample_id: str):
    try:
        alerts = service.get_alerts_by_sample(sample_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify([a.model_dump() for a in alerts]), 200


def confirm_alert(alert_id: str):
    try:
        alert = service.confirm_alert(alert_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(alert.model_dump()), 200