from my_project.db_init import db
from sqlalchemy import text

class AggregateDAO:
    @staticmethod
    def aggregate_column(table_name, column_name, operation):
        connection = db.engine.connect()
        try:
            query = text("CALL AggregateColumn(:table_name, :column_name, :operation)")
            connection.execute(query, {
                'table_name': table_name,
                'column_name': column_name,
                'operation': operation
            })

            connection.close()

            result_connection = db.engine.connect()
            result_query = text("SELECT @result")
            result = result_connection.execute(result_query).fetchone()

            result_connection.close()

            return result[0] if result else None
        except Exception as e:
            connection.close()
            raise e
