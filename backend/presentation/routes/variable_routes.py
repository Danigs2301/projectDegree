from flask import Blueprint
from presentation.controllers.variable_controller import (
    create_variable,
    get_variable,
    get_all_variables,
    delete_variable
)

variable_bp = Blueprint("variables", __name__, url_prefix="/variables")

variable_bp.post("/")(create_variable)
variable_bp.get("/")(get_all_variables)
variable_bp.get("/<variable_id>")(get_variable)
variable_bp.delete("/<variable_id>")(delete_variable)