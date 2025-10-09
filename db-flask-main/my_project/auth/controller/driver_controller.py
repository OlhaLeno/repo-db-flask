from flask import request, jsonify
from my_project.auth.service.driver_service import DriverService

driver_service = DriverService()

def get_all_drivers():
    """Get all drivers
    ---
    tags:
      - Drivers
    responses:
      200:
        description: List of all drivers
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              license_number:
                type: string
              phone:
                type: string
    """
    drivers = driver_service.get_all_drivers()
    return jsonify([driver.to_dict() for driver in drivers]), 200

def get_driver_by_id(driver_id):
    """Get a driver by ID
    ---
    tags:
      - Drivers
    parameters:
      - name: driver_id
        in: path
        type: integer
        required: true
        description: ID driver
    responses:
      200:
        description: Information about the driver
      404:
        description: Driver not found
    """
    driver = driver_service.get_driver_by_id(driver_id)
    if driver:
        return jsonify(driver.to_dict()), 200
    return jsonify({'message': 'Driver not found'}), 404

def create_driver():
    """Create a new driver
    ---
    tags:
      - Drivers
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            license_number:
              type: string
            phone:
              type: string
    responses:
      201:
        description: Driver successfully created
      400:
        description: Invalid data
    """
    data = request.get_json()
    new_driver = driver_service.create_driver(data)

    if isinstance(new_driver, dict) and new_driver.get('error'):
        return jsonify(new_driver), 400

    return jsonify(new_driver.to_dict()), 201

def update_driver(driver_id):
    """Update a driver
    ---
    tags:
      - Drivers
    parameters:
      - name: driver_id
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
            license_number:
              type: string
            phone:
              type: string
    responses:
      200:
        description: Driver successfully updated
      404:
        description: Driver not found
    """
    data = request.get_json()
    updated_driver = driver_service.update_driver(driver_id, data)
    if updated_driver:
        return jsonify(updated_driver.to_dict())
    return jsonify({"error": "Driver not found"}), 404

def delete_driver(driver_id):
    """Delete a driver
    ---
    tags:
      - Drivers
    parameters:
      - name: driver_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Driver deleted successfully
      404:
        description: Driver not found
    """
    success = driver_service.delete_driver(driver_id)
    if success:
        return jsonify({'message': 'Driver deleted successfully'}), 200
    return jsonify({'message': 'Driver not found'}), 404

def get_stats():
    """Get statistics about drivers
    ---
    tags:
      - Drivers
    parameters:
      - name: stat_type
        in: query
        type: string
        required: true
        description: Type of statistics (e.g., count, average, max, min)
    responses:
      200:
        description: Driver statistics
      400:
        description: Invalid stat_type parameter
    """
    stat_type = request.args.get('stat_type', default=None)
    if not stat_type:
        return jsonify({'error': 'stat_type is required'}), 400

    result = driver_service.get_driver_statistics(stat_type)
    if 'error' in result:
        return jsonify(result), 400

    return jsonify({'stat_type': stat_type, 'value': result}), 200
