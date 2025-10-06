from flask import Blueprint
from my_project.auth.controller.stop_controller import (
    get_all_stops, get_stop_by_id, create_stop, update_stop, delete_stop
)

stop_bp = Blueprint('stop', __name__)

stop_bp.route('/stops', methods=['GET'])(get_all_stops)
stop_bp.route('/stops/<int:stop_id>', methods=['GET'])(get_stop_by_id)
stop_bp.route('/stops', methods=['POST'])(create_stop)
stop_bp.route('/stops/<int:stop_id>', methods=['PUT'])(update_stop)
stop_bp.route('/stops/<int:stop_id>', methods=['DELETE'])(delete_stop)
