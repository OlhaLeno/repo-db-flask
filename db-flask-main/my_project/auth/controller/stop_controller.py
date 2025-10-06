from flask import request, jsonify
from my_project.auth.service.stop_service import StopService

stop_service = StopService()

def get_all_stops():
    """Отримати всі зупинки
    ---
    tags:
      - Stops
    responses:
      200:
        description: Список усіх зупинок
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
    """Отримати зупинку за ID
    ---
    tags:
      - Stops
    parameters:
      - name: stop_id
        in: path
        type: integer
        required: true
        description: ID зупинки
    responses:
      200:
        description: Інформація про зупинку
      404:
        description: Зупинку не знайдено
    """
    stop = stop_service.get_stop_by_id(stop_id)
    if stop:
        return jsonify(stop.to_dict()), 200
    return jsonify({'message': 'Stop not found'}), 404

def create_stop():
    """Створити нову зупинку
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
        description: Зупинку успішно створено
      400:
        description: Невірні дані або помилка тригера
    """
    data = request.json
    new_stop = stop_service.create_stop(data)
    if isinstance(new_stop, dict) and 'error' in new_stop:
        return jsonify(new_stop), 400
    return jsonify({'message': 'stop added successfully'}), 201

def update_stop(stop_id):
    """Оновити зупинку
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
        description: Зупинку оновлено
      400:
        description: Помилка тригера
      404:
        description: Зупинку не знайдено
    """
    data = request.json
    result= stop_service.update_stop(stop_id, data)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 400  # Повертаємо помилку тригера
    if result:
        return jsonify({'message': 'stop updated successfully', 'stop': result.to_dict()}), 200
    return jsonify({'message': 'stop not found'}), 404

def delete_stop(stop_id):
    """Видалити зупинку
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
        description: Зупинку видалено
      400:
        description: Помилка тригера
      404:
        description: Зупинку не знайдено
    """
    result = stop_service.delete_stop(stop_id)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 400
    if result:
        return jsonify({'message': 'stop deleted successfully'}), 200
    return jsonify({'message': 'stop not found'}), 404

