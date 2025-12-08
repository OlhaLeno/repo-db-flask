"""
Database Helper for DLQ operations
Shared functions for DB operations
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import pymssql


def parse_connection_string(conn_str: str) -> Dict[str, str]:
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
            elif key in ['initial catalog', 'database']:
                params['database'] = value.strip()
            elif key in ['user id', 'uid']:
                params['user'] = value.strip()
            elif key in ['password', 'pwd']:
                params['password'] = value.strip()
    
    return params


def get_db_connection(max_retries: int = 3, retry_delay: int = 2):
    """
    Create DB connection with retry logic
    
    Args:
        max_retries: Max retry attempts
        retry_delay: Delay between attempts (seconds)
        
    Returns:
        pymssql.Connection
        
    Raises:
        Exception: If connection failed after all attempts
    """
    conn_str = os.environ['SqlConnectionString']
    db_params = parse_connection_string(conn_str)
    
    logging.info(f"Connecting to: {db_params.get('server')}, database: {db_params.get('database')}")
    
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
            return conn
        except Exception as e:
            error_msg = str(e)
            logging.warning(f"Connection attempt {attempt + 1} failed: {error_msg}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logging.error(f"Failed to connect after {max_retries} attempts: {error_msg}")
                raise
    
    raise Exception("Failed to establish database connection after multiple retries")


def save_dlq_error(error_data: Dict[str, Any]) -> Optional[int]:
    """
    Save DLQ error to database
    
    Args:
        error_data: Error data
        
    Returns:
        ID of saved record or None if error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Extract enqueued_time from timestamp if available
            enqueued_time = datetime.utcnow()
            if 'timestamp' in error_data.get('original_message', ''):
                try:
                    import json
                    msg_data = json.loads(error_data['original_message'])
                    enqueued_time = datetime.fromisoformat(
                        msg_data['timestamp'].replace('Z', '+00:00')
                    )
                except:
                    pass
            
            cursor.execute("""
                INSERT INTO dlq_errors (
                    message_id, enqueued_time, original_message,
                    sensor_id, sensor_type, error_type, error_category,
                    error_message, error_details, stack_trace,
                    delivery_count, dead_letter_reason, dead_letter_error_description,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                SELECT SCOPE_IDENTITY();
            """,
                error_data.get('message_id'),
                enqueued_time,
                error_data.get('original_message'),
                error_data.get('sensor_id'),
                error_data.get('sensor_type'),
                error_data.get('error_type'),
                error_data.get('error_category'),
                error_data.get('error_message'),
                error_data.get('error_details'),
                error_data.get('stack_trace'),
                error_data.get('delivery_count', 0),
                error_data.get('dead_letter_reason'),
                error_data.get('dead_letter_error_description'),
                'pending'
            )
            
            # Get inserted record ID
            row = cursor.fetchone()
            error_id = int(row[0]) if row else None
            
            conn.commit()
            logging.info(f"DLQ error saved with ID: {error_id}")
            return error_id
            
        except Exception as e:
            logging.error(f"Error saving DLQ error: {str(e)}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        return None


def save_recovery_attempt(dlq_error_id: int, recovery_data: Dict[str, Any]) -> bool:
    """
    Save recovery attempt
    
    Args:
        dlq_error_id: DLQ error ID
        recovery_data: Recovery attempt data
        
    Returns:
        True if saved successfully
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO dlq_recovery (
                    dlq_error_id, recovery_method, recovery_status,
                    modified_message, recovery_notes, error_on_recovery,
                    performed_by
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                dlq_error_id,
                recovery_data.get('recovery_method'),
                recovery_data.get('recovery_status'),
                recovery_data.get('modified_message'),
                recovery_data.get('recovery_notes'),
                recovery_data.get('error_on_recovery'),
                recovery_data.get('performed_by', 'system')
            )
            
            # Update error record
            new_status = 'recovered' if recovery_data.get('recovery_status') == 'success' else 'failed'
            
            cursor.execute("""
                UPDATE dlq_errors
                SET recovery_attempts = recovery_attempts + 1,
                    last_recovery_attempt = GETUTCDATE(),
                    status = %s,
                    resolved_time = CASE WHEN %s = 'recovered' THEN GETUTCDATE() ELSE resolved_time END,
                    updated_at = GETUTCDATE()
                WHERE id = %s
            """,
                new_status,
                new_status,
                dlq_error_id
            )
            
            conn.commit()
            logging.info(f"Recovery attempt saved for DLQ error ID: {dlq_error_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving recovery attempt: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        return False


def get_pending_dlq_errors(limit: int = 100, 
                          error_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get pending DLQ errors for processing
    
    Args:
        limit: Max number of records
        error_type: Filter by error type
        
    Returns:
        List of errors
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(as_dict=True)
        
        try:
            query = """
                SELECT TOP (%s) *
                FROM dlq_errors
                WHERE status = 'pending'
            """
            params = [limit]
            
            if error_type:
                query += " AND error_type = %s"
                params.append(error_type)
            
            query += " ORDER BY dead_lettered_time ASC"
            
            cursor.execute(query, *params)
            errors = cursor.fetchall()
            
            return errors
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Error fetching pending DLQ errors: {str(e)}")
        return []


def get_dlq_statistics(time_period: str = '24h') -> Dict[str, Any]:
    """
    Get DLQ statistics
    
    Args:
        time_period: Period ('1h', '24h', '7d', '30d', 'all')
        
    Returns:
        Dictionary with statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(as_dict=True)
        
        try:
            # Call stored procedure
            cursor.callproc('sp_get_dlq_statistics', (time_period,))
            
            # First result - overall statistics
            stats = cursor.fetchone()
            
            # Second result - top errors
            cursor.nextset()
            top_errors = cursor.fetchall()
            
            # Third result - top problematic sensors
            cursor.nextset()
            top_sensors = cursor.fetchall()
            
            return {
                'overview': stats,
                'top_errors': top_errors,
                'top_problematic_sensors': top_sensors
            }
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Error fetching DLQ statistics: {str(e)}")
        return {}


def create_alert(alert_data: Dict[str, Any]) -> bool:
    """
    Create alert in database
    
    Args:
        alert_data: Alert data
        
    Returns:
        True if created successfully
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO dlq_alerts (
                    alert_type, alert_category, alert_message, alert_details,
                    dlq_error_id, affected_count, threshold_value, current_value
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                alert_data.get('alert_type'),
                alert_data.get('alert_category'),
                alert_data.get('alert_message'),
                alert_data.get('alert_details'),
                alert_data.get('dlq_error_id'),
                alert_data.get('affected_count'),
                alert_data.get('threshold_value'),
                alert_data.get('current_value')
            )
            
            conn.commit()
            logging.info(f"Alert created: {alert_data.get('alert_type')} - {alert_data.get('alert_category')}")
            return True
            
        except Exception as e:
            logging.error(f"Error creating alert: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        return False


def update_dlq_statistics_hourly():
    """
    Update hourly DLQ statistics
    Called from Timer trigger function
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(as_dict=True)
        
        try:
            current_time = datetime.utcnow()
            current_date = current_time.date()
            current_hour = current_time.hour
            
            # Get statistics for last hour
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_dead_lettered,
                    SUM(CASE WHEN error_type = 'transient' THEN 1 ELSE 0 END) as error_type_transient,
                    SUM(CASE WHEN error_type = 'validation' THEN 1 ELSE 0 END) as error_type_validation,
                    SUM(CASE WHEN error_type = 'business' THEN 1 ELSE 0 END) as error_type_business,
                    SUM(CASE WHEN error_type = 'system' THEN 1 ELSE 0 END) as error_type_system
                FROM dlq_errors
                WHERE dead_lettered_time >= DATEADD(HOUR, -1, GETUTCDATE())
            """)
            
            error_stats = cursor.fetchone()
            
            # Get recovery statistics
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN recovery_status = 'success' THEN 1 ELSE 0 END) as successful_recoveries,
                    SUM(CASE WHEN recovery_status = 'failed' THEN 1 ELSE 0 END) as failed_recoveries
                FROM dlq_recovery
                WHERE recovery_time >= DATEADD(HOUR, -1, GETUTCDATE())
            """)
            
            recovery_stats = cursor.fetchone()
            
            # Get pending recoveries
            cursor.execute("""
                SELECT COUNT(*) as pending_recoveries
                FROM dlq_errors
                WHERE status = 'pending'
                    AND dead_lettered_time >= DATEADD(HOUR, -1, GETUTCDATE())
            """)
            
            pending_stats = cursor.fetchone()
            
            # Get affected sensors
            cursor.execute("""
                SELECT DISTINCT sensor_id, sensor_type
                FROM dlq_errors
                WHERE dead_lettered_time >= DATEADD(HOUR, -1, GETUTCDATE())
                    AND sensor_id IS NOT NULL
            """)
            
            sensors = cursor.fetchall()
            
            # Format JSON for sensors
            import json
            affected_sensors = json.dumps([s['sensor_id'] for s in sensors])
            affected_sensor_types = json.dumps(list(set([s['sensor_type'] for s in sensors if s['sensor_type']])))
            
            # Insert or update statistics
            cursor.execute("""
                MERGE INTO dlq_statistics AS target
                USING (SELECT %s AS date, %s AS hour) AS source
                ON target.date = source.date AND target.hour = source.hour
                WHEN MATCHED THEN
                    UPDATE SET
                        total_dead_lettered = %s,
                        error_type_transient = %s,
                        error_type_validation = %s,
                        error_type_business = %s,
                        error_type_system = %s,
                        successful_recoveries = %s,
                        failed_recoveries = %s,
                        pending_recoveries = %s,
                        affected_sensors = %s,
                        affected_sensor_types = %s,
                        updated_at = GETUTCDATE()
                WHEN NOT MATCHED THEN
                    INSERT (date, hour, total_dead_lettered, error_type_transient,
                           error_type_validation, error_type_business, error_type_system,
                           successful_recoveries, failed_recoveries, pending_recoveries,
                           affected_sensors, affected_sensor_types)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
                current_date, current_hour,
                error_stats['total_dead_lettered'] or 0,
                error_stats['error_type_transient'] or 0,
                error_stats['error_type_validation'] or 0,
                error_stats['error_type_business'] or 0,
                error_stats['error_type_system'] or 0,
                recovery_stats['successful_recoveries'] or 0,
                recovery_stats['failed_recoveries'] or 0,
                pending_stats['pending_recoveries'] or 0,
                affected_sensors,
                affected_sensor_types,
                current_date, current_hour,
                error_stats['total_dead_lettered'] or 0,
                error_stats['error_type_transient'] or 0,
                error_stats['error_type_validation'] or 0,
                error_stats['error_type_business'] or 0,
                error_stats['error_type_system'] or 0,
                recovery_stats['successful_recoveries'] or 0,
                recovery_stats['failed_recoveries'] or 0,
                pending_stats['pending_recoveries'] or 0,
                affected_sensors,
                affected_sensor_types
            )
            
            conn.commit()
            logging.info(f"DLQ statistics updated for {current_date} {current_hour}:00")
            
        except Exception as e:
            logging.error(f"Error updating statistics: {str(e)}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")


# Export functions
__all__ = [
    'get_db_connection',
    'save_dlq_error',
    'save_recovery_attempt',
    'get_pending_dlq_errors',
    'get_dlq_statistics',
    'create_alert',
    'update_dlq_statistics_hourly'
]

