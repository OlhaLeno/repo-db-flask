import json
import logging
import os
import sys
import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.db_helpers import get_db_connection, save_recovery_attempt


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP API to recover messages from DLQ
    
    Query parameters:
    - error_id: ID of specific error to recover
    - error_type: Recover all errors of this type
    - date_from, date_to: Recover errors for period
    - sensor_id: Recover errors for specific sensor
    - limit: Max number of messages (default: 10)
    - dry_run: If true, only shows what will be recovered (default: false)
    """
    logging.info('Recover DLQ messages API called')
    
    try:
        # Get parameters
        error_id = req.params.get('error_id')
        error_type = req.params.get('error_type')
        sensor_id = req.params.get('sensor_id')
        date_from = req.params.get('date_from')
        date_to = req.params.get('date_to')
        limit = int(req.params.get('limit', '10'))
        dry_run = req.params.get('dry_run', 'false').lower() == 'true'
        
        # Validate parameters
        if not any([error_id, error_type, sensor_id, date_from]):
            return func.HttpResponse(
                json.dumps({
                    'error': 'At least one filter parameter required: error_id, error_type, sensor_id, or date_from',
                    'usage': {
                        'error_id': 'Recover specific error by ID',
                        'error_type': 'Recover all errors of type (transient, validation, business, system)',
                        'sensor_id': 'Recover errors for specific sensor',
                        'date_from': 'Recover errors from date (ISO format)',
                        'date_to': 'Recover errors until date (ISO format)',
                        'limit': 'Maximum number of messages to recover (default: 10, max: 100)',
                        'dry_run': 'If true, only show what would be recovered (default: false)'
                    }
                }, indent=2),
                status_code=400,
                mimetype='application/json'
            )
        
        # Limit max value
        limit = min(limit, 100)
        
        # Get errors for recovery
        errors_to_recover = get_errors_for_recovery(
            error_id=error_id,
            error_type=error_type,
            sensor_id=sensor_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        
        if not errors_to_recover:
            return func.HttpResponse(
                json.dumps({
                    'message': 'No errors found matching the criteria',
                    'recovered': 0
                }, indent=2),
                status_code=200,
                mimetype='application/json'
            )
        
        logging.info(f"Found {len(errors_to_recover)} errors to recover")
        
        # Dry run - only show what will be recovered
        if dry_run:
            preview = []
            for error in errors_to_recover:
                preview.append({
                    'error_id': error['id'],
                    'message_id': error['message_id'],
                    'sensor_id': error['sensor_id'],
                    'sensor_type': error['sensor_type'],
                    'error_type': error['error_type'],
                    'error_category': error['error_category'],
                    'dead_lettered_time': str(error['dead_lettered_time'])
                })
            
            return func.HttpResponse(
                json.dumps({
                    'dry_run': True,
                    'message': f'Would recover {len(errors_to_recover)} messages',
                    'errors': preview
                }, indent=2),
                status_code=200,
                mimetype='application/json'
            )
        
        # Actual recovery
        results = recover_messages(errors_to_recover)
        
        return func.HttpResponse(
            json.dumps({
                'message': f'Recovery completed',
                'total_found': len(errors_to_recover),
                'successful': results['successful'],
                'failed': results['failed'],
                'details': results['details']
            }, indent=2),
            status_code=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        logging.error(f"Error in recover_dlq_messages: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            }, indent=2),
            status_code=500,
            mimetype='application/json'
        )


def get_errors_for_recovery(error_id=None, error_type=None, sensor_id=None,
                            date_from=None, date_to=None, limit=10):
    """
    Get DLQ errors for recovery from DB
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(as_dict=True)
        
        try:
            # Build query
            query = """
                SELECT TOP (%s) *
                FROM dlq_errors
                WHERE status IN ('pending', 'failed')
            """
            params = [limit]
            
            if error_id:
                query += " AND id = %s"
                params.append(int(error_id))
            
            if error_type:
                query += " AND error_type = %s"
                params.append(error_type)
            
            if sensor_id:
                query += " AND sensor_id = %s"
                params.append(sensor_id)
            
            if date_from:
                query += " AND dead_lettered_time >= %s"
                params.append(date_from)
            
            if date_to:
                query += " AND dead_lettered_time <= %s"
                params.append(date_to)
            
            query += " ORDER BY dead_lettered_time ASC"
            
            cursor.execute(query, *params)
            errors = cursor.fetchall()
            
            return errors
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Error fetching errors for recovery: {str(e)}")
        return []


def recover_messages(errors):
    """
    Recover messages by sending them back to primary queue
    """
    results = {
        'successful': 0,
        'failed': 0,
        'details': []
    }
    
    try:
        # Connect to Service Bus
        connection_string = os.environ['ServiceBusConnection']
        queue_name = 'iot-sensor-data'
        
        with ServiceBusClient.from_connection_string(connection_string) as client:
            with client.get_queue_sender(queue_name) as sender:
                for error in errors:
                    error_id = error['id']
                    message_body = error['original_message']
                    
                    try:
                        # Create new message
                        message = ServiceBusMessage(message_body)
                        
                        # Add custom properties for tracking
                        message.application_properties = {
                            'recovered_from_dlq': True,
                            'original_message_id': error['message_id'],
                            'dlq_error_id': error_id,
                            'recovery_attempt': error['recovery_attempts'] + 1
                        }
                        
                        # Send to primary queue
                        sender.send_messages(message)
                        
                        # Save successful recovery attempt
                        recovery_data = {
                            'recovery_method': 'requeue',
                            'recovery_status': 'success',
                            'recovery_notes': f'Message requeued to {queue_name}',
                            'performed_by': 'api'
                        }
                        
                        save_recovery_attempt(error_id, recovery_data)
                        
                        results['successful'] += 1
                        results['details'].append({
                            'error_id': error_id,
                            'message_id': error['message_id'],
                            'sensor_id': error['sensor_id'],
                            'status': 'success'
                        })
                        
                        logging.info(f"Successfully recovered message {error['message_id']} (error_id: {error_id})")
                        
                    except Exception as e:
                        logging.error(f"Failed to recover message {error['message_id']}: {str(e)}")
                        
                        # Save failed attempt
                        recovery_data = {
                            'recovery_method': 'requeue',
                            'recovery_status': 'failed',
                            'error_on_recovery': str(e),
                            'recovery_notes': f'Failed to requeue: {str(e)}',
                            'performed_by': 'api'
                        }
                        
                        save_recovery_attempt(error_id, recovery_data)
                        
                        results['failed'] += 1
                        results['details'].append({
                            'error_id': error_id,
                            'message_id': error['message_id'],
                            'sensor_id': error['sensor_id'],
                            'status': 'failed',
                            'error': str(e)
                        })
        
    except Exception as e:
        logging.error(f"Error connecting to Service Bus: {str(e)}")
        results['failed'] = len(errors)
        results['details'].append({
            'status': 'failed',
            'error': f'Service Bus connection failed: {str(e)}'
        })
    
    return results

