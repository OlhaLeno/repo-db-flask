from flask import request, jsonify
from my_project.auth.service.stop_service import StopService

stop_service = StopService()

def get_all_stops():
    """Get all stops
    ---
    tags:
      - Stops
    responses:
      200:
        description: List of all stops
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              latitude:
                type: number
              longitude:
                type: number
    """
    stops = stop_service.get_all_stops()
    return jsonify([stop.to_dict() for stop in stops]), 200

def get_stop_by_id(stop_id):
    """Get a stop by ID
    ---
    tags:
      - Stops
    parameters:
      - name: stop_id
        in: path
        type: integer
        required: true
        description: ID stop
    responses:
      200:
        description: Information about the stop
      404:
        description: Stop not found
    """
    stop = stop_service.get_stop_by_id(stop_id)
    if stop:
        return jsonify(stop.to_dict()), 200
    return jsonify({'message': 'Stop not found'}), 404

def create_stop():
    """Create a new stop
    ---
    tags:
      - Stops
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            latitude:
              type: number
            longitude:
              type: number
    responses:
      201:
        description: Stop created successfully
      400:
        description: Invalid data or trigger error
    """
    data = request.json
    new_stop = stop_service.create_stop(data)
    if isinstance(new_stop, dict) and 'error' in new_stop:
        return jsonify(new_stop), 400
    return jsonify({'message': 'stop added successfully'}), 201

def update_stop(stop_id):
    """Update a stop
    ---
    tags:
      - Stops
    parameters:
      - name: stop_id
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
            latitude:
              type: number
            longitude:
              type: number
    responses:
      200:
        description: Stop updated successfully
      400:
        description: Trigger error
      404:
        description: Stop not found
    """
    data = request.json
    result= stop_service.update_stop(stop_id, data)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 400
    if result:
        return jsonify({'message': 'stop updated successfully', 'stop': result.to_dict()}), 200
    return jsonify({'message': 'stop not found'}), 404

def delete_stop(stop_id):
    """Delete a stop
    ---
    tags:
      - Stops
    parameters:
      - name: stop_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Stop deleted successfully
      400:
        description: Trigger error
      404:
        description: Stop not found
    """
    result = stop_service.delete_stop(stop_id)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 400
    if result:
        return jsonify({'message': 'stop deleted successfully'}), 200
    return jsonify({'message': 'stop not found'}), 404

