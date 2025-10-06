from flask import Blueprint
from my_project.auth.controller.route_controller import (
    get_all_routes, get_route_by_id, create_route, update_route, delete_route,insert_route_entries
)

route_bp = Blueprint('route', __name__)

route_bp.route('/routes', methods=['GET'])(get_all_routes)
route_bp.route('/routes/<int:route_id>', methods=['GET'])(get_route_by_id)
route_bp.route('/routes', methods=['POST'])(create_route)
route_bp.route('/routes/<int:route_id>', methods=['PUT'])(update_route)
route_bp.route('/routes/<int:route_id>', methods=['DELETE'])(delete_route)
route_bp.route('/routes/insert', methods=['POST'])(insert_route_entries)
