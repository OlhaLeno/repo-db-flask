from flask import Blueprint
from my_project.auth.controller.bus_controller import (
    get_all_buses, get_bus_by_id, create_bus, update_bus, delete_bus,get_buses_by_route,create_databases
)

bus_bp = Blueprint('bus', __name__)

bus_bp.route('/buses', methods=['GET'])(get_all_buses)
bus_bp.route('/buses/<int:bus_id>', methods=['GET'])(get_bus_by_id)
bus_bp.route('/buses', methods=['POST'])(create_bus)
bus_bp.route('/buses/<int:bus_id>', methods=['PUT'])(update_bus)
bus_bp.route('/buses/<int:bus_id>', methods=['DELETE'])(delete_bus)
bus_bp.route('/routes/<int:route_id>/buses', methods=['GET'])(get_buses_by_route)
bus_bp.route('/create-db', methods=['POST'])(create_databases)