from flask import request, jsonify
from my_project.auth.service.route_service import RouteService

route_service = RouteService()

def get_all_routes():
    """Отримати всі маршрути
    ---
    tags:
      - Routes
    responses:
      200:
        description: Список усіх маршрутів
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
    """Отримати маршрут за ID
    ---
    tags:
      - Routes
    parameters:
      - name: route_id
        in: path
        type: integer
        required: true
        description: ID маршруту
    responses:
      200:
        description: Інформація про маршрут
      404:
        description: Маршрут не знайдено
    """
    route = route_service.get_route_by_id(route_id)
    if route:
        return jsonify(route.to_dict()), 200
    return jsonify({'message': 'Route not found'}), 404

def create_route():
    """Створити новий маршрут
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
        description: Маршрут успішно створено
      400:
        description: Невірні дані
    """
    data = request.json
    new_route = route_service.create_route(data)
    return jsonify(new_route.to_dict()), 201

def update_route(route_id):
    """Оновити маршрут
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
        description: Маршрут оновлено
      404:
        description: Маршрут не знайдено
    """
    data = request.json
    updated_route = route_service.update_route(route_id, data)
    if updated_route:
        return jsonify(updated_route.to_dict()), 200
    return jsonify({'message': 'Route not found'}), 404

def delete_route(route_id):
    """Видалити маршрут
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
        description: Маршрут видалено
      404:
        description: Маршрут не знайдено
    """
    success = route_service.delete_route(route_id)
    if success:
        return jsonify({'message': 'Route deleted successfully'}), 200
    return jsonify({'message': 'Route not found'}), 404

def insert_route_entries():
    """Додати записи до маршруту
    ---
    tags:
      - Routes
    parameters:
      - name: body
        in: body
        required: true
        description: Дані для додавання записів до маршруту
    responses:
      200:
        description: Записи успішно додано
      400:
        description: Помилка при додаванні записів
    """
    response, status_code = route_service.insert_route_entries()
    return jsonify(response), status_code