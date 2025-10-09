from flask import Flask, jsonify, redirect, url_for
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import os

load_dotenv()

from __init__ import create_app

from my_project.auth.route.bus_routes import bus_bp
from my_project.auth.route.route_routes import route_bp
from my_project.auth.route.route_stop_routes import route_stop_bp
from my_project.auth.route.stop_routes import stop_bp
from my_project.auth.route.driver_routes import driver_bp
from my_project.auth.route.bus_inspection_route import inspection_bp
from my_project.auth.route.stats_route import stats_bp

app = create_app()

app.register_blueprint(bus_bp)
app.register_blueprint(driver_bp)
app.register_blueprint(route_bp)
app.register_blueprint(route_stop_bp)
app.register_blueprint(stop_bp)
app.register_blueprint(inspection_bp)
app.register_blueprint(stats_bp)

@app.route("/")
def root():
    return redirect("/apidocs")

@app.route("/healthz")
def healthz():
    """Health check endpoint.
    ---
    tags:
      - health
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
    """
    return jsonify({"status": "ok"}), 200

@app.errorhandler(OperationalError)
def handle_sql_error(error):
    if 'Inserting rows into stop is not allowed' in str(error):
        return jsonify({"error": "Inserting rows into stop is not allowed"}), 403
    elif 'Updating rows in stop is not allowed' in str(error):
        return jsonify({"error": "Updating rows in stop is not allowed"}), 403
    elif 'Deleting rows from stop is not allowed' in str(error):
        return jsonify({"error": "Deleting rows from stop is not allowed"}), 403
    else:
        return jsonify({"error": "Database error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)