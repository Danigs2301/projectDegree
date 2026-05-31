from flask import Blueprint
from presentation.controllers.detection_controller import detect

detection_bp = Blueprint("detection", __name__, url_prefix="/detection")

detection_bp.post("/")(detect)