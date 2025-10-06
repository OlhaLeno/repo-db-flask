from my_project.auth.dao.stop_dao import StopDAO

class StopService:
    def __init__(self):
        self.stop_dao = StopDAO()

    def get_all_stops(self):
        return self.stop_dao.get_all()

    def get_stop_by_id(self, stop_id):
        return self.stop_dao.get_by_id(stop_id)

    def create_stop(self, data):
        return self.stop_dao.create(data)

    def update_stop(self, stop_id, data):
        return self.stop_dao.update(stop_id, data)

    def delete_stop(self, stop_id):
        return self.stop_dao.delete(stop_id)
