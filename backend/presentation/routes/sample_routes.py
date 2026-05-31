from flask import Blueprint
from presentation.controllers.sample_controller import (
    create_sample,
    get_sample,
    get_samples_by_process,
    delete_sample
)

sample_bp = Blueprint("samples", __name__, url_prefix="/samples")

sample_bp.post("/")(create_sample)
sample_bp.get("/<sample_id>")(get_sample)
sample_bp.get("/process/<process_id>")(get_samples_by_process)
sample_bp.delete("/<sample_id>")(delete_sample)