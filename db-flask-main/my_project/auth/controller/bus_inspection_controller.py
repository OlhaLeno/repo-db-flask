# controllers/bus_inspection_controller.py
from flask import request, jsonify
from my_project.auth.service.bus_inspection_service import BusInspectionService

bus_inspection_service = BusInspectionService()

def get_all_inspections():
    """Get all bus inspections
    ---
    tags:
      - Bus Inspections
    responses:
      200:
        description: List of all bus inspections
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              bus_id:
                type: integer
              inspection_date:
                type: string
                format: date
              inspection_result:
                type: string
              remarks:
                type: string
    """
    inspections = bus_inspection_service.get_all_inspections()
    return jsonify([inspection.to_dict() for inspection in inspections]), 200

def get_inspection_by_id(inspection_id):
    """Get a bus inspection by ID
    ---
    tags:
      - Bus Inspections
    parameters:
      - name: inspection_id
        in: path
        type: integer
        required: true
        description: ID inspection
    responses:
      200:
        description: Information about the inspection
      404:
        description: Inspection not found
    """
    inspection = bus_inspection_service.get_inspection_by_id(inspection_id)
    if inspection:
        return jsonify(inspection.to_dict()), 200
    return jsonify({'message': 'Inspection not found'}), 404

def update_bus_inspection(inspection_id):
    """Update a bus inspection
    ---
    tags:
      - Bus Inspections
    parameters:
      - name: inspection_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            bus_id:
              type: integer
            inspection_date:
              type: string
              format: date
            inspection_result:
              type: string
            remarks:
              type: string
    responses:
      200:
        description: Inspection updated successfully
      404:
        description: Inspection not found
    """
    data = request.json
    updated_inspection = bus_inspection_service.update_bus_inspection(inspection_id, data)
    if updated_inspection:
        return jsonify(updated_inspection.to_dict()), 200
    return jsonify({'message': 'Inspection not found'}), 404

def delete_bus_inspection(inspection_id):
    """Delete a bus inspection
    ---
    tags:
      - Bus Inspections
    parameters:
      - name: inspection_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Inspection deleted successfully
      404:
        description: Inspection not found
    """
    success = bus_inspection_service.delete_bus_inspection(inspection_id)
    if success:
        return jsonify({'message': 'Inspection deleted successfully'}), 200
    return jsonify({'message': 'Inspection not found'}), 404

def get_inspections_by_bus_id(bus_id):
    """Get inspections by bus ID
    ---
    tags:
      - Bus Inspections
    parameters:
      - name: bus_id
        in: path
        type: integer
        required: true
        description: ID bus
    responses:
      200:
        description: List of bus inspections
    """
    inspections = bus_inspection_service.get_inspections_by_bus_id(bus_id)
    return jsonify([inspection.to_dict() for inspection in inspections]), 200


def create_bus_inspection():
    """Create a new bus inspection
    ---
    tags:
      - Bus Inspections
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            bus_id:
              type: integer
            inspection_date:
              type: string
              format: date
            inspection_result:
              type: string
            remarks:
              type: string
          required:
            - bus_id
            - inspection_date
            - inspection_result
    responses:
      201:
        description: Bus inspection created successfully
      400:
        description: Invalid data or missing required fields
      500:
        description: Server error
    """
    data = request.get_json()

    bus_id = data.get('bus_id')
    inspection_date = data.get('inspection_date')
    inspection_result = data.get('inspection_result')
    remarks = data.get('remarks')

    if not bus_id or not inspection_date or not inspection_result:
        return jsonify({"message": "Missing required fields"}), 400

    try:
        bus_inspection_service.create_inspection(bus_id, inspection_date, inspection_result, remarks)
        return jsonify({"message": "Bus inspection record created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500