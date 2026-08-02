from flask import Blueprint
from presentation.controllers.summary_controller import (
    get_all_summaries,
    get_process_summary
)

summary_bp = Blueprint("summary", __name__, url_prefix="/summary")

summary_bp.get("/")(get_all_summaries)
summary_bp.get("/<process_id>")(get_process_summary)