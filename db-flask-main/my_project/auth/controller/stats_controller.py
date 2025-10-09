from flask import request, jsonify
from my_project.auth.service.stats_service import AggregateService

aggregate_service = AggregateService()


def get_column_stat():
    """Get aggregate statistics for a table column
    ---
    tags:
      - Statistics
    parameters:
      - name: table_name
        in: query
        type: string
        required: true
        description: Table name
      - name: column_name
        in: query
        type: string
        required: true
        description: Column name
      - name: operation
        in: query
        type: string
        required: true
        description: Operation type (SUM, AVG, MAX, MIN, COUNT)
        enum:
          - SUM
          - AVG
          - MAX
          - MIN
          - COUNT
    responses:
      200:
        description: Result of the aggregate operation
        schema:
          type: object
          properties:
            result:
              type: number
      400:
        description: Invalid parameters or execution error
      500:
        description: Error executing aggregation
    """
    table_name = request.args.get('table_name')
    column_name = request.args.get('column_name')
    operation = request.args.get('operation')

    if not table_name or not column_name or not operation:
        return jsonify({"message": "Missing required parameters"}), 400

    try:
        result = aggregate_service.get_column_stat(table_name, column_name, operation)
        if result is None:
            return jsonify({"message": "Error executing aggregation"}), 500
        return jsonify({"result": result}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500