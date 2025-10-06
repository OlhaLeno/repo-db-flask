from flask import request, jsonify
from my_project.auth.service.driver_service import DriverService

driver_service = DriverService()

def get_all_drivers():
    """Отримати всіх водіїв
    ---
    tags:
      - Drivers
    responses:
      200:
        description: Список усіх водіїв
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
    """Отримати водія за ID
    ---
    tags:
      - Drivers
    parameters:
      - name: driver_id
        in: path
        type: integer
        required: true
        description: ID водія
    responses:
      200:
        description: Інформація про водія
      404:
        description: Водія не знайдено
    """
    driver = driver_service.get_driver_by_id(driver_id)
    if driver:
        return jsonify(driver.to_dict()), 200
    return jsonify({'message': 'Driver not found'}), 404

def create_driver():
    """Створити нового водія
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
        description: Водія успішно створено
      400:
        description: Невірні дані
    """
    data = request.get_json()
    new_driver = driver_service.create_driver(data)

    # Якщо сталася помилка, повертаємо її в JSON форматі
    if isinstance(new_driver, dict) and new_driver.get('error'):
        return jsonify(new_driver), 400

    # Якщо створено водія, повертаємо його дані у відповіді
    return jsonify(new_driver.to_dict()), 201

def update_driver(driver_id):
    """Оновити водія
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
        description: Водія оновлено
      404:
        description: Водія не знайдено
    """
    data = request.get_json()
    updated_driver = driver_service.update_driver(driver_id, data)
    if updated_driver:
        return jsonify(updated_driver.to_dict())
    return jsonify({"error": "Driver not found"}), 404

def delete_driver(driver_id):
    """Видалити водія
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
        description: Водія видалено
      404:
        description: Водія не знайдено
    """
    success = driver_service.delete_driver(driver_id)
    if success:
        return jsonify({'message': 'Driver deleted successfully'}), 200
    return jsonify({'message': 'Driver not found'}), 404

def get_stats():
    """Отримати статистику по водіях
    ---
    tags:
      - Drivers
    parameters:
      - name: stat_type
        in: query
        type: string
        required: true
        description: Тип статистики (наприклад, count, average, max, min)
    responses:
      200:
        description: Статистика водіїв
      400:
        description: Невірний параметр stat_type
    """
    # Отримуємо тип статистики з параметрів запиту
    stat_type = request.args.get('stat_type', default=None)
    if not stat_type:
        return jsonify({'error': 'stat_type is required'}), 400

    # Отримуємо статистику для водіїв
    result = driver_service.get_driver_statistics(stat_type)
    if 'error' in result:
        return jsonify(result), 400

    return jsonify({'stat_type': stat_type, 'value': result}), 200
