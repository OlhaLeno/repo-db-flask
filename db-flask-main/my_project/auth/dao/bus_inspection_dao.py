# dao/bus_inspection_dao.py
from my_project.db_init import db
from my_project.auth.models.bus_inspection import BusInspection
from my_project.auth.dao.bus_dao import BusDAO
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text  # Імпортуємо text для роботи з SQL запитами


class BusInspectionDAO:
    def __init__(self):
        self.bus_dao = BusDAO()

    def get_all(self):
        """Отримує всі огляди автобуса"""
        return BusInspection.query.all()

    def get_by_id(self, inspection_id):
        """Отримує огляд автобуса за його ID"""
        return BusInspection.query.get(inspection_id)

    def create(self, data):
        """Створює новий огляд автобуса, перевіряючи наявність автобуса"""
        bus_id = data.get('bus_id')
        # Перевіряємо наявність автобуса в таблиці bus
        bus = self.bus_dao.get_by_id(bus_id)
        if not bus:
            raise ValueError("Bus with the specified ID does not exist.")

        new_inspection = BusInspection(**data)
        try:
            db.session.add(new_inspection)
            db.session.commit()
            return new_inspection
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def update(self, inspection_id, data):
        """Оновлює огляд автобуса за ID"""
        inspection = BusInspection.query.get(inspection_id)
        if inspection:
            for key, value in data.items():
                setattr(inspection, key, value)
            db.session.commit()
            return inspection
        return None

    def delete(self, inspection_id):
        """Видаляє огляд автобуса за ID"""
        inspection = BusInspection.query.get(inspection_id)
        if inspection:
            db.session.delete(inspection)
            db.session.commit()
            return True
        return False

    def get_by_bus_id(self, bus_id):
        """Отримує всі огляди для конкретного автобуса"""
        return BusInspection.query.filter_by(bus_id=bus_id).all()

    def insert_bus_inspection(self, bus_id, inspection_date, inspection_result, remarks):
        # Використовуємо text() для оголошення SQL запиту
        sql = text("""
            CALL insert_bus_inspection(:bus_id, :inspection_date, :inspection_result, :remarks)
        """)
        # Виконуємо запит із параметрами
        db.session.execute(sql, {
            'bus_id': bus_id,
            'inspection_date': inspection_date,
            'inspection_result': inspection_result,
            'remarks': remarks
        })
        db.session.commit()