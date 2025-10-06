# controllers/bus_inspection_controller.py
from flask import request, jsonify
from my_project.auth.service.bus_inspection_service import BusInspectionService

bus_inspection_service = BusInspectionService()

def get_all_inspections():
    """Отримати всі огляди автобусів
    ---
    tags:
      - Bus Inspections
    responses:
      200:
        description: Список усіх оглядів автобусів
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
    """Отримати огляд автобуса за ID
    ---
    tags:
      - Bus Inspections
    parameters:
      - name: inspection_id
        in: path
        type: integer
        required: true
        description: ID огляду
    responses:
      200:
        description: Інформація про огляд
      404:
        description: Огляд не знайдено
    """
    inspection = bus_inspection_service.get_inspection_by_id(inspection_id)
    if inspection:
        return jsonify(inspection.to_dict()), 200
    return jsonify({'message': 'Inspection not found'}), 404

def update_bus_inspection(inspection_id):
    """Оновити огляд автобуса
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
        description: Огляд оновлено
      404:
        description: Огляд не знайдено
    """
    data = request.json
    updated_inspection = bus_inspection_service.update_bus_inspection(inspection_id, data)
    if updated_inspection:
        return jsonify(updated_inspection.to_dict()), 200
    return jsonify({'message': 'Inspection not found'}), 404

def delete_bus_inspection(inspection_id):
    """Видалити огляд автобуса
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
        description: Огляд видалено
      404:
        description: Огляд не знайдено
    """
    success = bus_inspection_service.delete_bus_inspection(inspection_id)
    if success:
        return jsonify({'message': 'Inspection deleted successfully'}), 200
    return jsonify({'message': 'Inspection not found'}), 404

def get_inspections_by_bus_id(bus_id):
    """Отримати огляди за ID автобуса
    ---
    tags:
      - Bus Inspections
    parameters:
      - name: bus_id
        in: path
        type: integer
        required: true
        description: ID автобуса
    responses:
      200:
        description: Список оглядів автобуса
    """
    inspections = bus_inspection_service.get_inspections_by_bus_id(bus_id)
    return jsonify([inspection.to_dict() for inspection in inspections]), 200


def create_bus_inspection():
    """Створити новий огляд автобуса
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
        description: Огляд автобуса створено
      400:
        description: Невірні дані або відсутні обов'язкові поля
      500:
        description: Помилка сервера
    """
    data = request.get_json()

    # Отримуємо дані з запиту
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