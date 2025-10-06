from flask import Blueprint
from my_project.auth.controller.route_stop_controller import (
    get_all_route_stops, get_route_stop_by_id, create_route_stop, update_route_stop, delete_route_stop,get_route_stops_by_route,insert_route_stop
)

route_stop_bp = Blueprint('route_stop', __name__)

route_stop_bp.route('/route_stops', methods=['GET'])(get_all_route_stops)
route_stop_bp.route('/route_stops/<int:route_stop_id>', methods=['GET'])(get_route_stop_by_id)
route_stop_bp.route('/route_stops', methods=['POST'])(create_route_stop)
route_stop_bp.route('/route_stops/<int:route_stop_id>', methods=['PUT'])(update_route_stop)
route_stop_bp.route('/route_stops/<int:route_stop_id>', methods=['DELETE'])(delete_route_stop)
route_stop_bp.route('/route_stops/route/<int:route_id>', methods=['GET'])(get_route_stops_by_route)
route_stop_bp.route('/route_stop', methods=['POST'])(insert_route_stop)