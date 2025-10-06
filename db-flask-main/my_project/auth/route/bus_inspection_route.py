from flask import Blueprint
from my_project.auth.controller.bus_inspection_controller import (
    get_all_inspections, get_inspection_by_id, create_bus_inspection, update_bus_inspection, delete_bus_inspection, get_inspections_by_bus_id,
)

inspection_bp = Blueprint('inspection', __name__)

inspection_bp.route('/inspections', methods=['GET'])(get_all_inspections)
inspection_bp.route('/inspections/<int:inspection_id>', methods=['GET'])(get_inspection_by_id)
inspection_bp.route('/inspections', methods=['POST'])(create_bus_inspection)
inspection_bp.route('/inspections/<int:inspection_id>', methods=['PUT'])(update_bus_inspection)
inspection_bp.route('/inspections/<int:inspection_id>', methods=['DELETE'])(delete_bus_inspection)
inspection_bp.route('/buses/<int:bus_id>/inspections', methods=['GET'])(get_inspections_by_bus_id)
