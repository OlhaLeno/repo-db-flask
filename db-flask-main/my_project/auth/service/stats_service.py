from my_project.auth.dao.Stats_dao import AggregateDAO

class AggregateService:
    def __init__(self):
        self.aggregate_dao = AggregateDAO()

    def get_column_stat(self, table_name, column_name, operation):
        # Перевірка на коректність параметрів
        if operation not in ['MAX', 'MIN', 'AVG', 'SUM']:
            raise ValueError("Invalid operation. Allowed operations: MAX, MIN, AVG, SUM.")

        # Викликаємо DAO для отримання статистики
        return self.aggregate_dao.aggregate_column(table_name, column_name, operation)