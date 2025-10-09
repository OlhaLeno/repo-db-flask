from flask import request, jsonify
from my_project.auth.service.bus_service import BusService

bus_service = BusService()

def get_all_buses():
    """Get all buses
    ---
    tags:
      - Buses
    responses:
      200:
        description: List of all buses
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              license_plate:
                type: string
              model:
                type: string
              capacity:
                type: integer
    """
    buses = bus_service.get_all_buses()
    return jsonify([bus.to_dict() for bus in buses]), 200

def get_bus_by_id(bus_id):
    """Get a bus by ID
    ---
    tags:
      - Buses
    parameters:
      - name: bus_id
        in: path
        type: integer
        required: true
        description: ID bus
    responses:
      200:
        description: Information about the bus
      404:
        description: Bus not found
    """
    bus = bus_service.get_bus_by_id(bus_id)
    if bus:
        return jsonify(bus.to_dict()), 200
    return jsonify({'message': 'Bus not found'}), 404

def create_bus():
    """Create a new bus
    ---
    tags:
      - Buses
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            license_plate:
              type: string
            model:
              type: string
            capacity:
              type: integer
            route_id:
              type: integer
    responses:
      201:
        description: Bus created successfully
      400:
        description: Invalid data
    """
    data = request.json
    new_bus = bus_service.create_bus(data)
    return jsonify(new_bus.to_dict()), 201

def update_bus(bus_id):
    """Update a bus
    ---
    tags:
      - Buses
    parameters:
      - name: bus_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            license_plate:
              type: string
            model:
              type: string
            capacity:
              type: integer
            route_id:
              type: integer
    responses:
      200:
        description: Bus updated successfully
      404:
        description: Bus not found
    """
    data = request.json
    updated_bus = bus_service.update_bus(bus_id, data)
    if updated_bus:
        return jsonify(updated_bus.to_dict()), 200
    return jsonify({'message': 'Bus not found'}), 404

def delete_bus(bus_id):
    """Delete a bus
    ---
    tags:
      - Buses
    parameters:
      - name: bus_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Bus deleted successfully
      404:
        description: Bus not found
    """
    success = bus_service.delete_bus(bus_id)
    if success:
        return jsonify({'message': 'Bus deleted successfully'}), 200
    return jsonify({'message': 'Bus not found'}), 404

def get_buses_by_route(route_id):
    """Get buses by route
    ---
    tags:
      - Buses
    parameters:
      - name: route_id
        in: path
        type: integer
        required: true
        description: ID route
    responses:
      200:
        description: List of buses on the route
    """
    buses = bus_service.get_buses_by_route(route_id)
    return jsonify([bus.to_dict() for bus in buses]), 200

def create_databases():
    """Create database structure
    ---
    tags:
      - Database
    responses:
      200:
        description: Database created successfully
      500:
        description: Error creating database
    """
    response = bus_service.create_databases()

    if isinstance(response, dict) and 'error' in response:
        return jsonify(response), 500

    return jsonify(response), 200