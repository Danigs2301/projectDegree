from flask import Blueprint
from presentation.controllers.model_controller import (
    create_model,
    get_model,
    get_models_by_process,
    delete_model,
    get_training_data,
    train_model
)

model_bp = Blueprint("models", __name__, url_prefix="/models")

model_bp.post("/")(create_model)
model_bp.get("/<model_id>")(get_model)
model_bp.get("/process/<process_id>")(get_models_by_process)
model_bp.delete("/<model_id>")(delete_model)
model_bp.get("/process/<process_id>/training-data")(get_training_data)
model_bp.post("/<model_id>/train")(train_model)