# my_project/auth/dao/driver_dao.py
from my_project.db_init import db
from my_project.auth.models.driver import Driver
from sqlalchemy.exc import OperationalError
from sqlalchemy import func


class DriverDAO:
    def __init__(self):
        self.db_session = db.session

    def validate_phone_number(self, phone_number):
        """Phone number verification (cannot end in '00')"""
        if phone_number.endswith("00"):
            return False
        return True

    def get_all(self):
        """Gets all drivers"""
        try:
            return Driver.query.all()
        except OperationalError as e:
            return {'error': f"Error fetching drivers: {str(e)}"}

    def get_by_id(self, driver_id):
        """Gets a driver by ID"""
        try:
            return Driver.query.get(driver_id)
        except OperationalError as e:
            return {'error': f"Error fetching driver: {str(e)}"}

    def create(self, data):
        """Creates a new driver"""
        phone_number = data.get("phone_number")

        if not self.validate_phone_number(phone_number):
            return {'error': 'Phone number cannot end with 00'}

        try:
            new_driver = Driver(**data)
            self.db_session.add(new_driver)
            self.db_session.commit()
            return new_driver
        except OperationalError as e:
            self.db_session.rollback()
            return {'error': f"Error creating driver: {str(e)}"}

    def update(self, driver_id, data):
        """Updates driver data"""
        try:
            driver = Driver.query.get(driver_id)
            if driver:
                for key, value in data.items():
                    setattr(driver, key, value)
                self.db_session.commit()
                return driver
            return None
        except OperationalError as e:
            return {'error': f"Error updating driver: {str(e)}"}

    def delete(self, driver_id):
        """Deletes a driver by ID"""
        try:
            driver = Driver.query.get(driver_id)
            if driver:
                self.db_session.delete(driver)
                self.db_session.commit()
                return True
            return False
        except OperationalError as e:
            return {'error': f"Error deleting driver: {str(e)}"}

    def get_driver_stats(self, stat_type):
        """Gets statistics for drivers"""
        if stat_type == 'MAX':
            return self.db_session.query(func.max(Driver.driver_id)).scalar()

        elif stat_type == 'MIN':
            return self.db_session.query(func.min(Driver.driver_id)).scalar()

        elif stat_type == 'AVG':
            return self.db_session.query(func.avg(Driver.experience_years)).scalar()

        elif stat_type == 'COUNT':
            return self.db_session.query(func.count(Driver.driver_id)).scalar()

        elif stat_type == 'SUM':
            return self.db_session.query(func.sum(Driver.experience_years)).scalar()

        else:
            return {'error': 'Invalid stat_type'}