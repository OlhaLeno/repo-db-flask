import json
import logging
import os
import sys
import time
import azure.functions as func
import pymssql

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.dlq_helpers import MessageValidator, ErrorClassifier

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

def main(msg: func.ServiceBusMessage) -> None:
    """
    Process message from Service Bus Queue
    On error Azure automatically moves to DLQ after maxDeliveryCount attempts
    """
    message_body = msg.get_body().decode('utf-8')
    message_id = msg.message_id
    delivery_count = msg.delivery_count
    
    logging.info(f'Service Bus queue trigger processing message: {message_id} (delivery #{delivery_count})')
    logging.info(f'Message body: {message_body}')
    
    try:
        # Parse message
        try:
            data = json.loads(message_body)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in message {message_id}: {str(e)}")
            # Validation error - don't retry, throw exception to move to DLQ
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        # Validate data using MessageValidator
        is_valid, validation_error = MessageValidator.validate_message(data)
        if not is_valid:
            logging.error(f"Validation error for message {message_id}: {validation_error}")
            # Validation error - throw exception to move to DLQ
            raise ValueError(f"Validation failed: {validation_error}")
        
        # Connect to DB via pymssql with retry logic
        conn_str = os.environ['SqlConnectionString']
        db_params = parse_connection_string(conn_str)
        
        logging.info(f"Connecting to: {db_params.get('server')}, database: {db_params.get('database')}")
        
        max_retries = 3
        retry_delay = 2
        conn = None
        last_error = None
        
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
                last_error = e
                error_msg = str(e)
                error_type, error_category = ErrorClassifier.classify_error(e)
                
                logging.warning(
                    f"Connection attempt {attempt + 1}/{max_retries} failed: {error_msg} "
                    f"(type: {error_type}, category: {error_category})"
                )
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logging.error(
                        f"Failed to connect after {max_retries} attempts. "
                        f"Message will be moved to DLQ after max delivery count."
                    )
                    # Throw transient error for retry in Service Bus
                    raise ConnectionError(f"Database connection failed after {max_retries} attempts: {error_msg}")
        
        if conn is None:
            raise ConnectionError(f"Failed to establish database connection: {str(last_error)}")
        
        cursor = conn.cursor()
        
        try:
            # Insert data (pymssql uses %s instead of ?)
            cursor.execute("""
                INSERT INTO sensor_data (sensor_id, sensor_type, value, latitude, longitude, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, 
                data['sensor_id'], 
                data['sensor_type'], 
                float(data['value']),
                float(data['latitude']), 
                float(data['longitude']), 
                data['timestamp']
            )
            
            conn.commit()
            logging.info(
                f"✓ Data saved successfully: {data['sensor_id']} ({data['sensor_type']}) = {data['value']} "
                f"[{data['latitude']}, {data['longitude']}] at {data['timestamp']}"
            )
            
        except Exception as e:
            error_type, error_category = ErrorClassifier.classify_error(e)
            logging.error(
                f"Database error: {str(e)} (type: {error_type}, category: {error_category})"
            )
            conn.rollback()
            
            # If constraint violation (e.g. duplicate), this is business error
            if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                # Don't retry for duplicates
                raise ValueError(f"Duplicate data: {str(e)}")
            
            # Other DB errors - transient, allow retry
            raise
        finally:
            cursor.close()
            conn.close()
            
    except ValueError as e:
        # Validation or business logic errors - log and throw for DLQ
        logging.error(f"Validation/Business error for message {message_id}: {str(e)}")
        raise
        
    except ConnectionError as e:
        # Transient errors - log and throw for retry
        logging.error(f"Transient error for message {message_id}: {str(e)}")
        raise
    
    except Exception as e:
        # Other errors - log with full stack
        error_type, error_category = ErrorClassifier.classify_error(e)
        logging.error(
            f"Unexpected error processing message {message_id}: {str(e)} "
            f"(type: {error_type}, category: {error_category})",
            exc_info=True
        )
        # Throw to move to DLQ
        raise
