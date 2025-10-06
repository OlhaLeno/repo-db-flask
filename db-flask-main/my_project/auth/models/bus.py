# models/bus.py

from my_project.db_init import db

class Bus(db.Model):
    __tablename__ = 'bus'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    model = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=True)

    route = db.relationship('Route', back_populates='buses')

    # Відношення з таблицею BusInspection
    inspections = db.relationship('BusInspection', back_populates='bus')

    def to_dict(self):
        return {
            'id': self.id,
            'license_plate': self.license_plate,
            'model': self.model,
            'capacity': self.capacity,
            'route_id': self.route_id,
            'inspections': [inspection.to_dict() for inspection in self.inspections] if self.inspections else []
        }
