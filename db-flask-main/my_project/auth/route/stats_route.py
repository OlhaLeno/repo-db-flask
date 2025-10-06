from flask import Blueprint
from my_project.auth.controller.stats_controller import get_column_stat

stats_bp = Blueprint('stats', __name__)

stats_bp.route('/aggregate', methods=['GET'])(get_column_stat)
