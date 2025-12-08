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
    logging.info('HTTP trigger function processed a request.')
    
    try:
        # Get request parameters
        sensor_type = req.params.get('sensor_type')
        sensor_id = req.params.get('sensor_id')
        limit = int(req.params.get('limit', 100))
        
        # Validate limit
        if limit > 1000:
            limit = 1000
        if limit < 1:
            limit = 1
        
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
            # Build query (pymssql uses %s instead of ?)
            query = f"SELECT TOP ({limit}) id, sensor_id, sensor_type, value, latitude, longitude, timestamp FROM sensor_data WHERE 1=1"
            params = []
            
            if sensor_type:
                query += " AND sensor_type = %s"
                params.append(sensor_type)
            
            if sensor_id:
                query += " AND sensor_id = %s"
                params.append(sensor_id)
            
            query += " ORDER BY timestamp DESC"
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            
            # Build result
            result = []
            for row in rows:
                result.append({
                    'id': row[0],
                    'sensor_id': row[1],
                    'sensor_type': row[2],
                    'value': float(row[3]),
                    'latitude': float(row[4]),
                    'longitude': float(row[5]),
                    'timestamp': row[6].isoformat() if hasattr(row[6], 'isoformat') else str(row[6])
                })
            
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
