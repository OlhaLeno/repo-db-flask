from my_project.auth.dao.route_stop_dao import RouteStopDAO
from flask import request, jsonify

class RouteStopService:
    def __init__(self):
        self.route_stop_dao = RouteStopDAO()

    def get_all_route_stops(self):
        return self.route_stop_dao.get_all()

    def get_route_stops_by_route(self, route_id):
        return self.route_stop_dao.get_route_stops_by_route(route_id)
    def get_route_stop_by_id(self, route_stop_id):
        return self.route_stop_dao.get_by_id(route_stop_id)

    def create_route_stop(self, data):
        return self.route_stop_dao.create(data)

    def update_route_stop(self, route_stop_id, data):
        return self.route_stop_dao.update(route_stop_id, data)

    def delete_route_stop(self, route_stop_id):
        return self.route_stop_dao.delete(route_stop_id)

    def insert_route_stop(self, route_id, stop_id, price_from_previous):
        """Інтерфейс для вставки RouteStop через DAO"""
        return self.route_stop_dao.insert_route_stop(route_id, stop_id, price_from_previous)
