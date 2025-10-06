from flask import request, jsonify
from my_project.auth.service.bus_service import BusService

bus_service = BusService()

def get_all_buses():
    """Отримати всі автобуси
    ---
    tags:
      - Buses
    responses:
      200:
        description: Список усіх автобусів
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
    """Отримати автобус за ID
    ---
    tags:
      - Buses
    parameters:
      - name: bus_id
        in: path
        type: integer
        required: true
        description: ID автобуса
    responses:
      200:
        description: Інформація про автобус
      404:
        description: Автобус не знайдено
    """
    bus = bus_service.get_bus_by_id(bus_id)
    if bus:
        return jsonify(bus.to_dict()), 200
    return jsonify({'message': 'Bus not found'}), 404

def create_bus():
    """Створити новий автобус
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
        description: Автобус успішно створено
      400:
        description: Невірні дані
    """
    data = request.json
    new_bus = bus_service.create_bus(data)
    return jsonify(new_bus.to_dict()), 201

def update_bus(bus_id):
    """Оновити автобус
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
        description: Автобус оновлено
      404:
        description: Автобус не знайдено
    """
    data = request.json
    updated_bus = bus_service.update_bus(bus_id, data)
    if updated_bus:
        return jsonify(updated_bus.to_dict()), 200
    return jsonify({'message': 'Bus not found'}), 404

def delete_bus(bus_id):
    """Видалити автобус
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
        description: Автобус видалено
      404:
        description: Автобус не знайдено
    """
    success = bus_service.delete_bus(bus_id)
    if success:
        return jsonify({'message': 'Bus deleted successfully'}), 200
    return jsonify({'message': 'Bus not found'}), 404

def get_buses_by_route(route_id):
    """Отримати автобуси за маршрутом
    ---
    tags:
      - Buses
    parameters:
      - name: route_id
        in: path
        type: integer
        required: true
        description: ID маршруту
    responses:
      200:
        description: Список автобусів на маршруті
    """
    buses = bus_service.get_buses_by_route(route_id)
    return jsonify([bus.to_dict() for bus in buses]), 200

def create_databases():
    """Створити структуру бази даних
    ---
    tags:
      - Database
    responses:
      200:
        description: База даних створена
      500:
        description: Помилка створення бази даних
    """
    response = bus_service.create_databases()

    # Перевіряємо, чи є 'response' словником і чи містить він ключ 'error'
    if isinstance(response, dict) and 'error' in response:
        return jsonify(response), 500

    # Якщо все в порядку, повертаємо успішну відповідь
    return jsonify(response), 200