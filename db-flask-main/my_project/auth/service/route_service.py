from my_project.auth.dao.route_dao import RouteDAO
from sqlalchemy.exc import SQLAlchemyError

class RouteService:
    def __init__(self):
        self.route_dao = RouteDAO()

    def get_all_routes(self):
        return self.route_dao.get_all()

    def get_route_by_id(self, route_id):
        return self.route_dao.get_by_id(route_id)

    def create_route(self, data):
        return self.route_dao.create(data)

    def update_route(self, route_id, data):
        return self.route_dao.update(route_id, data)

    def delete_route(self, route_id):
        return self.route_dao.delete(route_id)

    def insert_route_entries(self):
        try:
            # Викликаємо DAO метод для вставки записів
            self.route_dao.insert_route_entries()
            return {"message": "10 route entries inserted successfully!"}, 200
        except Exception as e:
            return {"message": str(e)}, 500