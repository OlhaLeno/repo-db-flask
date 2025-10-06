from flask import Blueprint
from my_project.auth.controller.driver_controller import (
    get_all_drivers, get_driver_by_id, create_driver, update_driver, delete_driver,
get_stats
)

driver_bp = Blueprint('driver', __name__)

driver_bp.route('/drivers', methods=['GET'])(get_all_drivers)
driver_bp.route('/drivers/<int:driver_id>', methods=['GET'])(get_driver_by_id)
driver_bp.route('/drivers', methods=['POST'])(create_driver)
driver_bp.route('/drivers/<int:driver_id>', methods=['PUT'])(update_driver)
driver_bp.route('/drivers/<int:driver_id>', methods=['DELETE'])(delete_driver)
driver_bp.route('/drivers/stats', methods=['GET'])(get_stats)
