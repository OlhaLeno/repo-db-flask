from database import db

class GeneralDAO:
    def __init__(self, model):
        self.model = model

    def get_all(self):
        return self.model.query.all()

    def get_by_id(self, id):
        return self.model.query.get(id)

    def create(self, data):
        instance = self.model(**data)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, id, data):
        instance = self.model.query.get(id)
        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
            db.session.commit()
            return instance
        return None

    def delete(self, id):
        instance = self.model.query.get(id)
        if instance:
            db.session.delete(instance)
            db.session.commit()
            return True
        return False
