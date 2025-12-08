import json
import logging
import os
import sys
import azure.functions as func

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.dlq_helpers import ErrorClassifier, DLQLogger, create_alert_message
from shared.db_helpers import save_dlq_error, save_recovery_attempt, create_alert


def main(msg: func.ServiceBusMessage) -> None:
    """
    Process messages from Dead Letter Queue
    Logs errors, analyzes causes and attempts recovery where possible
    """
    message_body = msg.get_body().decode('utf-8')
    message_id = msg.message_id
    
    # Get DLQ metadata
    dead_letter_reason = msg.dead_letter_reason
    dead_letter_error_description = msg.dead_letter_error_description
    delivery_count = msg.delivery_count
    enqueued_time = msg.enqueued_time_utc
    
    logging.info(f'Processing DLQ message: {message_id}')
    logging.info(f'Dead letter reason: {dead_letter_reason}')
    logging.info(f'Error description: {dead_letter_error_description}')
    logging.info(f'Delivery count: {delivery_count}')
    logging.info(f'Message body: {message_body}')
    
    try:
        # Parse original message for analysis
        original_data = None
        try:
            original_data = json.loads(message_body)
            logging.info(f"Original message parsed: sensor={original_data.get('sensor_id')}, type={original_data.get('sensor_type')}")
        except json.JSONDecodeError:
            logging.warning("Failed to parse original message as JSON")
        
        # Classify error based on DLQ metadata
        error_type, error_category = classify_dlq_error(
            dead_letter_reason,
            dead_letter_error_description,
            message_body
        )
        
        logging.info(f"Error classified as: type={error_type}, category={error_category}")
        
        # Create structured error log
        error_data = {
            'message_id': message_id,
            'original_message': message_body,
            'sensor_id': original_data.get('sensor_id') if original_data else None,
            'sensor_type': original_data.get('sensor_type') if original_data else None,
            'error_type': error_type,
            'error_category': error_category,
            'error_message': dead_letter_error_description or dead_letter_reason,
            'error_details': f"Dead letter reason: {dead_letter_reason}. Description: {dead_letter_error_description}",
            'stack_trace': None,  # Stack trace not available from DLQ
            'delivery_count': delivery_count,
            'dead_letter_reason': dead_letter_reason,
            'dead_letter_error_description': dead_letter_error_description
        }
        
        # Save to DB
        error_id = save_dlq_error(error_data)
        
        if error_id:
            logging.info(f"DLQ error saved to database with ID: {error_id}")
            
            # Check if alert needed
            should_alert, alert_level = DLQLogger.should_alert(
                error_type, error_category, delivery_count
            )
            
            if should_alert:
                alert_message = create_alert_message('system_error' if error_type == 'system' else 'error_detected', error_data)
                
                alert_data = {
                    'alert_type': alert_level,
                    'alert_category': f'dlq_{error_type}',
                    'alert_message': alert_message,
                    'alert_details': json.dumps({
                        'message_id': message_id,
                        'error_type': error_type,
                        'error_category': error_category,
                        'sensor_id': error_data.get('sensor_id'),
                        'delivery_count': delivery_count
                    }),
                    'dlq_error_id': error_id,
                    'affected_count': 1,
                    'threshold_value': 10 if alert_level == 'critical' else 5,
                    'current_value': delivery_count
                }
                
                if create_alert(alert_data):
                    logging.info(f"Alert created: {alert_level} - {alert_message}")
            
            # Check if can auto-recover
            if ErrorClassifier.should_auto_recover(error_type, error_category, 0):
                logging.info(f"Message {message_id} is eligible for auto-recovery")
                
                # Here can add auto-recovery logic
                # For now just log - actual recovery done via separate function
                recovery_data = {
                    'recovery_method': 'auto_retry',
                    'recovery_status': 'pending',
                    'recovery_notes': 'Marked for automatic retry',
                    'performed_by': 'system'
                }
                save_recovery_attempt(error_id, recovery_data)
            else:
                logging.info(f"Message {message_id} requires manual review (type: {error_type})")
        else:
            logging.error("Failed to save DLQ error to database")
        
        # Log summary
        logging.info(
            f"DLQ message processed: "
            f"ID={message_id}, "
            f"Type={error_type}, "
            f"Category={error_category}, "
            f"Sensor={error_data.get('sensor_id', 'unknown')}, "
            f"DeliveryCount={delivery_count}"
        )
        
    except Exception as e:
        logging.error(f"Error processing DLQ message {message_id}: {str(e)}", exc_info=True)
        # Don't throw exception - don't want DLQ message to go to DLQ again


def classify_dlq_error(dead_letter_reason: str, 
                      dead_letter_description: str,
                      message_body: str) -> tuple:
    """
    Classify error based on DLQ metadata
    
    Returns:
        (error_type, error_category)
    """
    reason = (dead_letter_reason or '').lower()
    description = (dead_letter_description or '').lower()
    combined = f"{reason} {description}"
    
    # MaxDeliveryCountExceeded means many attempts
    if 'maxdeliverycount' in reason or 'exceeded' in reason:
        # Analyze description to determine original error
        if any(kw in description for kw in ['timeout', 'connection', 'network', 'unavailable']):
            return ErrorClassifier.ERROR_TYPE_TRANSIENT, ErrorClassifier.CATEGORY_DB_CONNECTION
        elif any(kw in description for kw in ['json', 'parse', 'format']):
            return ErrorClassifier.ERROR_TYPE_VALIDATION, ErrorClassifier.CATEGORY_INVALID_JSON
        elif any(kw in description for kw in ['validation', 'invalid', 'missing']):
            return ErrorClassifier.ERROR_TYPE_VALIDATION, ErrorClassifier.CATEGORY_MISSING_FIELDS
        elif any(kw in description for kw in ['duplicate', 'unique']):
            return ErrorClassifier.ERROR_TYPE_BUSINESS, ErrorClassifier.CATEGORY_DUPLICATE
        else:
            return ErrorClassifier.ERROR_TYPE_TRANSIENT, ErrorClassifier.CATEGORY_UNKNOWN
    
    # TTL expired
    if 'ttl' in combined or 'expired' in combined:
        return ErrorClassifier.ERROR_TYPE_BUSINESS, 'message_expired'
    
    # Session errors
    if 'session' in combined:
        return ErrorClassifier.ERROR_TYPE_SYSTEM, 'session_error'
    
    # Default - system error
    return ErrorClassifier.ERROR_TYPE_SYSTEM, ErrorClassifier.CATEGORY_UNKNOWN

