from flask import request, jsonify
from my_project.auth.service.route_stop_service import RouteStopService

route_stop_service = RouteStopService()

def get_all_route_stops():
    """Get all route stops
    ---
    tags:
      - Route Stops
    responses:
      200:
        description: List of all route stops
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              route_id:
                type: integer
              stop_id:
                type: integer
              price_from_previous:
                type: number
    """
    route_stops = route_stop_service.get_all_route_stops()
    return jsonify([route_stop.to_dict() for route_stop in route_stops]), 200

def get_route_stops_by_route(route_id):
    """Get stops by route
    ---
    tags:
      - Route Stops
    parameters:
      - name: route_id
        in: path
        type: integer
        required: true
        description: ID route
    responses:
      200:
        description: List of stops for the route
    """
    route_stops = route_stop_service.get_route_stops_by_route(route_id)
    return jsonify([rs.stop.to_dict() for rs in route_stops]), 200

def get_route_stop_by_id(route_stop_id):
    """Get route stop by ID
    ---
    tags:
      - Route Stops
    parameters:
      - name: route_stop_id
        in: path
        type: integer
        required: true
        description: ID route stop
    responses:
      200:
        description: Information about the route stop
      404:
        description: Route stop not found
    """
    route_stop = route_stop_service.get_route_stop_by_id(route_stop_id)
    if route_stop:
        return jsonify(route_stop.to_dict()), 200
    return jsonify({'message': 'Route Stop not found'}), 404

def create_route_stop():
    """Create a route stop
    ---
    tags:
      - Route Stops
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            route_id:
              type: integer
            stop_id:
              type: integer
            price_from_previous:
              type: number
    responses:
      201:
        description: Route stop created successfully
      400:
        description: Invalid data
    """
    data = request.json
    new_route_stop = route_stop_service.create_route_stop(data)
    return jsonify(new_route_stop.to_dict()), 201

def update_route_stop(route_stop_id):
    """Update a route stop
    ---
    tags:
      - Route Stops
    parameters:
      - name: route_stop_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            route_id:
              type: integer
            stop_id:
              type: integer
            price_from_previous:
              type: number
    responses:
      200:
        description: Route stop updated successfully
      404:
        description: Route stop not found
    """
    data = request.json
    updated_route_stop = route_stop_service.update_route_stop(route_stop_id, data)
    if updated_route_stop:
        return jsonify(updated_route_stop.to_dict()), 200
    return jsonify({'message': 'Route Stop not found'}), 404

def delete_route_stop(route_stop_id):
    """Delete a route stop
    ---
    tags:
      - Route Stops
    parameters:
      - name: route_stop_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Route stop deleted successfully
      404:
        description: Route stop not found
    """
    success = route_stop_service.delete_route_stop(route_stop_id)
    if success:
        return jsonify({'message': 'Route Stop deleted successfully'}), 200
    return jsonify({'message': 'Route Stop not found'}), 404


def insert_route_stop():
    """Insert a stop into a route (stored procedure)
    ---
    tags:
      - Route Stops
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            route_id:
              type: integer
            stop_id:
              type: integer
            price_from_previous:
              type: number
          required:
            - route_id
            - stop_id
            - price_from_previous
    responses:
      200:
        description: Route stop successfully added to the route
      400:
        description: Missing required parameters
    """
    data = request.get_json()

    route_id = data.get('route_id')
    stop_id = data.get('stop_id')
    price_from_previous = data.get('price_from_previous')

    if not route_id or not stop_id or price_from_previous is None:
        return jsonify({"error": "Missing required parameters"}), 400

    result, status_code = route_stop_service.insert_route_stop(
        route_id, stop_id, price_from_previous
    )

    return jsonify(result), status_code