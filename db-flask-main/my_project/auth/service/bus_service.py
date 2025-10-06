from my_project.auth.dao.bus_dao import BusDAO

class BusService:
    def __init__(self):
        self.bus_dao = BusDAO()

    def get_all_buses(self):
        return self.bus_dao.get_all()

    def get_bus_by_id(self, bus_id):
        return self.bus_dao.get_by_id(bus_id)

    def create_bus(self, data):
        return self.bus_dao.create(data)

    def update_bus(self, bus_id, data):
        return self.bus_dao.update(bus_id, data)

    def delete_bus(self, bus_id):
        return self.bus_dao.delete(bus_id)

    def get_buses_by_route(self, route_id):

        return self.bus_dao.get_buses_by_route(route_id)

    def create_databases(self):
        return self.bus_dao.create_databases_from_buses()