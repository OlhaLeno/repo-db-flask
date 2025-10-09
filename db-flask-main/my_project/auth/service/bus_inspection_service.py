# service/bus_inspection_service.py
from my_project.auth.dao.bus_inspection_dao import BusInspectionDAO

class BusInspectionService:
    def __init__(self):
        self.bus_inspection_dao = BusInspectionDAO()

    def get_all_inspections(self):
        """Gets all bus reviews"""
        return self.bus_inspection_dao.get_all()

    def get_inspection_by_id(self, inspection_id):
        """Gets a bus review by ID"""
        return self.bus_inspection_dao.get_by_id(inspection_id)

    def create_bus_inspection(self, data):
        """Creates a new bus review"""
        return self.bus_inspection_dao.create(data)

    def update_bus_inspection(self, inspection_id, data):
        """Updates an existing bus review"""
        return self.bus_inspection_dao.update(inspection_id, data)

    def delete_bus_inspection(self, inspection_id):
        """Deletes a bus review by ID"""
        return self.bus_inspection_dao.delete(inspection_id)

    def get_inspections_by_bus_id(self, bus_id):
        """Gets all reviews for a specific bus"""
        return self.bus_inspection_dao.get_by_bus_id(bus_id)

    def create_inspection(self, bus_id, inspection_date, inspection_result, remarks):
        self.bus_inspection_dao.insert_bus_inspection(bus_id, inspection_date, inspection_result, remarks)