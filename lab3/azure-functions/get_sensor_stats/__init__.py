import json
import logging
import os
import time
import azure.functions as func
import pymssql

def parse_connection_string(conn_str):
    """Parse connection string and return parameters for pymssql"""
    params = {}
    parts = conn_str.split(';')
    
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            key = key.strip().lower()
            
            if key == 'server':
                server = value.replace('tcp://', '').replace('tcp:', '').strip()
                if ',' in server:
                    server = server.split(',')[0]
                params['server'] = server
            elif key == 'initial catalog' or key == 'database':
                params['database'] = value.strip()
            elif key == 'user id' or key == 'uid':
                params['user'] = value.strip()
            elif key == 'password' or key == 'pwd':
                params['password'] = value.strip()
    
    return params

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function (get_sensor_stats) processed a request.')
    
    try:
        # Get request parameters
        sensor_type = req.params.get('sensor_type')
        sensor_id = req.params.get('sensor_id')
        time_period = req.params.get('time_period', '24h')  # Default last 24 hours
        
        # Determine time interval
        time_conditions = {
            '1h': 'timestamp >= DATEADD(HOUR, -1, GETUTCDATE())',
            '24h': 'timestamp >= DATEADD(HOUR, -24, GETUTCDATE())',
            '7d': 'timestamp >= DATEADD(DAY, -7, GETUTCDATE())',
            '30d': 'timestamp >= DATEADD(DAY, -30, GETUTCDATE())',
            'all': '1=1'
        }
        
        time_filter = time_conditions.get(time_period, time_conditions['24h'])
        
        # Connect to DB via pymssql
        conn_str = os.environ['SqlConnectionString']
        db_params = parse_connection_string(conn_str)
        
        logging.info(f"Connecting to: {db_params.get('server')}, database: {db_params.get('database')}")
        
        # Connect with retry logic
        max_retries = 3
        retry_delay = 2
        conn = None
        
        # For Azure SQL need to use user@server format
        user_with_server = db_params['user']
        if '@' not in user_with_server:
            user_with_server = f"{db_params['user']}@{db_params['server']}"
        
        for attempt in range(max_retries):
            try:
                conn = pymssql.connect(
                    server=db_params['server'],
                    user=user_with_server,
                    password=db_params['password'],
                    database=db_params['database'],
                    timeout=30,
                    login_timeout=30
                )
                logging.info("Successfully connected to database")
                break
            except Exception as e:
                error_msg = str(e)
                logging.warning(f"Connection attempt {attempt + 1} failed: {error_msg}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logging.error(f"Failed to connect after {max_retries} attempts: {error_msg}")
                    raise
        
        if conn is None:
            raise Exception("Failed to establish database connection after multiple retries.")
        
        cursor = conn.cursor()
        
        try:
            # Build query for statistics
            query = f"""
                SELECT 
                    sensor_type,
                    sensor_id,
                    COUNT(*) as count,
                    AVG(value) as avg_value,
                    MIN(value) as min_value,
                    MAX(value) as max_value,
                    MIN(timestamp) as first_reading,
                    MAX(timestamp) as last_reading
                FROM sensor_data
                WHERE {time_filter}
            """
            params = []
            
            if sensor_type:
                query += " AND sensor_type = %s"
                params.append(sensor_type)
            
            if sensor_id:
                query += " AND sensor_id = %s"
                params.append(sensor_id)
            
            query += " GROUP BY sensor_type, sensor_id ORDER BY sensor_type, sensor_id"
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            
            # Build result
            result = {
                'time_period': time_period,
                'statistics': []
            }
            
            for row in rows:
                result['statistics'].append({
                    'sensor_type': row[0],
                    'sensor_id': row[1],
                    'count': row[2],
                    'avg_value': round(float(row[3]), 2) if row[3] is not None else None,
                    'min_value': float(row[4]) if row[4] is not None else None,
                    'max_value': float(row[5]) if row[5] is not None else None,
                    'first_reading': row[6].isoformat() if hasattr(row[6], 'isoformat') else str(row[6]),
                    'last_reading': row[7].isoformat() if hasattr(row[7], 'isoformat') else str(row[7])
                })
            
            # Overall statistics
            total_query = f"""
                SELECT 
                    COUNT(*) as total_readings,
                    COUNT(DISTINCT sensor_id) as total_sensors,
                    COUNT(DISTINCT sensor_type) as total_sensor_types
                FROM sensor_data
                WHERE {time_filter}
            """
            
            if sensor_type or sensor_id:
                total_params = []
                if sensor_type:
                    total_query += " AND sensor_type = %s"
                    total_params.append(sensor_type)
                if sensor_id:
                    total_query += " AND sensor_id = %s"
                    total_params.append(sensor_id)
                cursor.execute(total_query, total_params)
            else:
                cursor.execute(total_query)
                
            total_row = cursor.fetchone()
            result['summary'] = {
                'total_readings': total_row[0],
                'total_sensors': total_row[1],
                'total_sensor_types': total_row[2]
            }
            
            return func.HttpResponse(
                json.dumps(result, indent=2),
                status_code=200,
                mimetype="application/json"
            )
            
        except Exception as e:
            logging.error(f"Database error: {str(e)}")
            return func.HttpResponse(
                json.dumps({'error': f'Database error: {str(e)}'}),
                status_code=500,
                mimetype="application/json"
            )
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=400,
            mimetype="application/json"
        )

