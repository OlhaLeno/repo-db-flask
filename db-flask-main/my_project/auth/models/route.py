from my_project.db_init import db


class Route(db.Model):
    __tablename__ = 'route'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    start_point = db.Column(db.String(255), nullable=False)
    end_point = db.Column(db.String(255), nullable=False)

    buses = db.relationship('Bus', back_populates='route', cascade='all, delete-orphan')
    route_stops = db.relationship('RouteStop', back_populates='route')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_point': self.start_point,
            'end_point': self.end_point,
            'stops': [rs.stop.to_dict() for rs in self.route_stops] if self.route_stops else []
        }
