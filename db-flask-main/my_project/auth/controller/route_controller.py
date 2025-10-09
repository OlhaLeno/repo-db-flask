from flask import request, jsonify
from my_project.auth.service.route_service import RouteService

route_service = RouteService()

def get_all_routes():
    """Get all routes
    ---
    tags:
      - Routes
    responses:
      200:
        description: List of all routes
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              start_point:
                type: string
              end_point:
                type: string
    """
    routes = route_service.get_all_routes()
    return jsonify([route.to_dict() for route in routes]), 200

def get_route_by_id(route_id):
    """Get a route by ID
    ---
    tags:
      - Routes
    parameters:
      - name: route_id
        in: path
        type: integer
        required: true
        description: ID route
    responses:
      200:
        description: Information about the route
      404:
        description: Route not found
    """
    route = route_service.get_route_by_id(route_id)
    if route:
        return jsonify(route.to_dict()), 200
    return jsonify({'message': 'Route not found'}), 404

def create_route():
    """Create a new route
    ---
    tags:
      - Routes
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            start_point:
              type: string
            end_point:
              type: string
    responses:
      201:
        description: Route successfully created
      400:
        description: Invalid data
    """
    data = request.json
    new_route = route_service.create_route(data)
    return jsonify(new_route.to_dict()), 201

def update_route(route_id):
    """Update a route
    ---
    tags:
      - Routes
    parameters:
      - name: route_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            start_point:
              type: string
            end_point:
              type: string
    responses:
      200:
        description: Route successfully updated
      404:
        description: Route not found
    """
    data = request.json
    updated_route = route_service.update_route(route_id, data)
    if updated_route:
        return jsonify(updated_route.to_dict()), 200
    return jsonify({'message': 'Route not found'}), 404

def delete_route(route_id):
    """Delete a route
    ---
    tags:
      - Routes
    parameters:
      - name: route_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Route deleted successfully
      404:
        description: Route not found
    """
    success = route_service.delete_route(route_id)
    if success:
        return jsonify({'message': 'Route deleted successfully'}), 200
    return jsonify({'message': 'Route not found'}), 404

def insert_route_entries():
    """Insert entries into a route
    ---
    tags:
      - Routes
    parameters:
      - name: body
        in: body
        required: true
        description: Data for adding entries to the route
    responses:
      200:
        description: Entries successfully added
      400:
        description: Error adding entries
    """
    response, status_code = route_service.insert_route_entries()
    return jsonify(response), status_code