from my_project.db_init import db
from my_project.auth.models.route_stop import RouteStop
from sqlalchemy import text



class RouteStopDAO:
    def get_all(self):
        return RouteStop.query.all()

    def get_by_id(self, route_stop_id):
        return RouteStop.query.get(route_stop_id)

    def get_route_stops_by_route(self, route_id):
        return RouteStop.query.filter_by(route_id=route_id).all()

    def create(self, data):
        new_route_stop = RouteStop(**data)
        db.session.add(new_route_stop)
        db.session.commit()
        return new_route_stop

    def update(self, route_stop_id, data):
        route_stop = RouteStop.query.get(route_stop_id)
        if route_stop:
            for key, value in data.items():
                setattr(route_stop, key, value)
            db.session.commit()
            return route_stop
        return None

    def delete(self, route_stop_id):
        route_stop = RouteStop.query.get(route_stop_id)
        if route_stop:
            db.session.delete(route_stop)
            db.session.commit()
            return True
        return False

    from sqlalchemy import text
    from my_project.db_init import db


    def insert_route_stop(self, route_id, stop_id, price_from_previous):
        # Створюємо SQL-запит для виклику збереженої процедури
        sql = text("""
            CALL insert_route_stop(:route_id, :stop_id, :price_from_previous)
        """)

        try:
            # Виконуємо запит
            db.session.execute(sql, {'route_id': route_id, 'stop_id': stop_id, 'price_from_previous': price_from_previous})
            db.session.commit()
            return {"message": "Route stop inserted successfully."}, 200
        except Exception as e:
            db.session.rollback()  # У разі помилки виконуємо відкат
            return {"error": str(e)}, 500