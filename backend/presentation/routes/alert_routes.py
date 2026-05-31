from flask import Blueprint
from presentation.controllers.alert_controller import (
    create_alert,
    get_alert,
    get_alerts_by_model,
    get_alerts_by_sample,
    confirm_alert
)

alert_bp = Blueprint("alerts", __name__, url_prefix="/alerts")

alert_bp.post("/")(create_alert)
alert_bp.get("/<alert_id>")(get_alert)
alert_bp.get("/model/<model_id>")(get_alerts_by_model)
alert_bp.get("/sample/<sample_id>")(get_alerts_by_sample)
alert_bp.patch("/<alert_id>/confirm")(confirm_alert)