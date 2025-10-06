# models/bus_inspection.py

from my_project.db_init import db

class BusInspection(db.Model):
    __tablename__ = 'bus_inspection'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    inspection_date = db.Column(db.DateTime, nullable=False)
    inspection_result = db.Column(db.String(100), nullable=False)
    remarks = db.Column(db.String(200), nullable=True)

    # Встановлюємо відношення з таблицею Bus
    bus = db.relationship('Bus', back_populates='inspections')

    def to_dict(self):
        return {
            'id': self.id,
            'bus_id': self.bus_id,
            'inspection_date': self.inspection_date.isoformat() if self.inspection_date else None,
            'inspection_result': self.inspection_result,
            'remarks': self.remarks,
        }

