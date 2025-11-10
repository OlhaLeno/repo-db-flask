from my_project.auth.dao.driver_dao import DriverDAO

class DriverService:
    def __init__(self):
        self.driver_dao = DriverDAO()

    def create_driver(self, data):
        try:
            return self.driver_dao.create(data)
        except Exception as e:
            return {"error": str(e)}

    def get_all_drivers(self):
        return self.driver_dao.get_all()

    def get_driver_by_id(self, driver_id):
        return self.driver_dao.get_by_id(driver_id)

    def update_driver(self, driver_id, data):
        return self.driver_dao.update(driver_id, data)

    def delete_driver(self, driver_id):
        return self.driver_dao.delete(driver_id)

    def get_driver_statistics(self, stat_type: str):
        result = self.driver_dao.get_driver_stats(stat_type)
        if isinstance(result, dict) and 'error' in result:
            return result
        return {'stat_type': stat_type, 'value': result}