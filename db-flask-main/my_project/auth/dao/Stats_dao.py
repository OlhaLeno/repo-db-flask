from my_project.db_init import db
from sqlalchemy import text

class AggregateDAO:
    @staticmethod
    def aggregate_column(table_name, column_name, operation):
        # Виконання збереженої процедури через окреме з'єднання
        connection = db.engine.connect()
        try:
            # Викликаємо збережену процедуру
            query = text("CALL AggregateColumn(:table_name, :column_name, :operation)")
            connection.execute(query, {
                'table_name': table_name,
                'column_name': column_name,
                'operation': operation
            })

            # Очищаємо потік після виконання процедури
            connection.close()

            # Тепер знову використовуємо нове з'єднання для отримання результату
            result_connection = db.engine.connect()
            result_query = text("SELECT @result")
            result = result_connection.execute(result_query).fetchone()

            # Закриваємо друге з'єднання
            result_connection.close()

            # Повертаємо результат
            return result[0] if result else None
        except Exception as e:
            # Якщо сталася помилка, закриваємо з'єднання і виводимо помилку
            connection.close()
            raise e
