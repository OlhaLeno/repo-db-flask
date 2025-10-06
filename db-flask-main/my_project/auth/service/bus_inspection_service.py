# service/bus_inspection_service.py
from my_project.auth.dao.bus_inspection_dao import BusInspectionDAO

class BusInspectionService:
    def __init__(self):
        self.bus_inspection_dao = BusInspectionDAO()

    def get_all_inspections(self):
        """Отримує всі огляди автобусів"""
        return self.bus_inspection_dao.get_all()

    def get_inspection_by_id(self, inspection_id):
        """Отримує огляд автобуса за ID"""
        return self.bus_inspection_dao.get_by_id(inspection_id)

    def create_bus_inspection(self, data):
        """Створює новий огляд для автобуса"""
        return self.bus_inspection_dao.create(data)

    def update_bus_inspection(self, inspection_id, data):
        """Оновлює існуючий огляд автобуса"""
        return self.bus_inspection_dao.update(inspection_id, data)

    def delete_bus_inspection(self, inspection_id):
        """Видаляє огляд автобуса за ID"""
        return self.bus_inspection_dao.delete(inspection_id)

    def get_inspections_by_bus_id(self, bus_id):
        """Отримує всі огляди для конкретного автобуса"""
        return self.bus_inspection_dao.get_by_bus_id(bus_id)

    def create_inspection(self, bus_id, inspection_date, inspection_result, remarks):
        self.bus_inspection_dao.insert_bus_inspection(bus_id, inspection_date, inspection_result, remarks)