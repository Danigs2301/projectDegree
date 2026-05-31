from flask import Blueprint
from presentation.controllers.process_controller import (
    create_process,
    get_process,
    get_all_processes,
    delete_process,
    assign_variable
)

process_bp = Blueprint("processes", __name__, url_prefix="/processes")

process_bp.post("/")(create_process)
process_bp.get("/")(get_all_processes)
process_bp.get("/<process_id>")(get_process)
process_bp.delete("/<process_id>")(delete_process)
process_bp.post("/<process_id>/variables")(assign_variable)