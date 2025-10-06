from my_project.db_init import db

class RouteStop(db.Model):
    __tablename__ = 'route_stop'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    stop_id = db.Column(db.Integer, db.ForeignKey('stop.id'), nullable=False)
    price_from_previous = db.Column(db.Numeric(10, 2), default=0.00)
    sequence_order = db.Column(db.Integer, default=1)

    route = db.relationship('Route', back_populates='route_stops')
    stop = db.relationship('Stop', back_populates='route_stops')
    
    def to_dict(self):
        return {
            'id': self.id,
            'route_id': self.route_id,
            'stop_id': self.stop_id,
            'price_from_previous': float(self.price_from_previous) if self.price_from_previous else 0.0,
            'sequence_order': self.sequence_order
        }
