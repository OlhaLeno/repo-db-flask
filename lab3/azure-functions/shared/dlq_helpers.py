"""
DLQ Helper Functions
Shared logic for Dead Letter Queue processing
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import traceback

class ErrorClassifier:
    """Error classifier for DLQ"""
    
    # Error types
    ERROR_TYPE_TRANSIENT = "transient"
    ERROR_TYPE_VALIDATION = "validation"
    ERROR_TYPE_BUSINESS = "business"
    ERROR_TYPE_SYSTEM = "system"
    
    # Error categories
    CATEGORY_DB_CONNECTION = "db_connection"
    CATEGORY_DB_TIMEOUT = "db_timeout"
    CATEGORY_INVALID_JSON = "invalid_json"
    CATEGORY_MISSING_FIELDS = "missing_fields"
    CATEGORY_INVALID_DATA_TYPE = "invalid_data_type"
    CATEGORY_INVALID_VALUE_RANGE = "invalid_value_range"
    CATEGORY_UNKNOWN_SENSOR = "unknown_sensor"
    CATEGORY_DUPLICATE = "duplicate"
    CATEGORY_CODE_ERROR = "code_error"
    CATEGORY_PERMISSION_DENIED = "permission_denied"
    CATEGORY_UNKNOWN = "unknown"
    
    @staticmethod
    def classify_error(error: Exception, message: Optional[Dict] = None) -> Tuple[str, str]:
        """
        Classify error and return (error_type, error_category)
        
        Args:
            error: Exception об'єкт
            message: Оригінальне повідомлення (якщо є)
            
        Returns:
            (error_type, error_category)
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Transient errors
        if any(keyword in error_str for keyword in [
            'timeout', 'connection', 'network', 'unavailable',
            'connection reset', 'connection refused', 'rate limit'
        ]):
            if 'timeout' in error_str:
                return (ErrorClassifier.ERROR_TYPE_TRANSIENT, 
                       ErrorClassifier.CATEGORY_DB_TIMEOUT)
            else:
                return (ErrorClassifier.ERROR_TYPE_TRANSIENT, 
                       ErrorClassifier.CATEGORY_DB_CONNECTION)
        
        # Validation errors
        if error_type == 'JSONDecodeError' or 'json' in error_str:
            return (ErrorClassifier.ERROR_TYPE_VALIDATION, 
                   ErrorClassifier.CATEGORY_INVALID_JSON)
        
        if error_type == 'KeyError' or 'missing' in error_str:
            return (ErrorClassifier.ERROR_TYPE_VALIDATION, 
                   ErrorClassifier.CATEGORY_MISSING_FIELDS)
        
        if error_type in ['TypeError', 'ValueError']:
            return (ErrorClassifier.ERROR_TYPE_VALIDATION, 
                   ErrorClassifier.CATEGORY_INVALID_DATA_TYPE)
        
        # Business logic errors
        if 'unknown sensor' in error_str or 'invalid sensor' in error_str:
            return (ErrorClassifier.ERROR_TYPE_BUSINESS, 
                   ErrorClassifier.CATEGORY_UNKNOWN_SENSOR)
        
        if 'duplicate' in error_str or 'unique constraint' in error_str:
            return (ErrorClassifier.ERROR_TYPE_BUSINESS, 
                   ErrorClassifier.CATEGORY_DUPLICATE)
        
        if 'range' in error_str or 'out of bounds' in error_str:
            return (ErrorClassifier.ERROR_TYPE_BUSINESS, 
                   ErrorClassifier.CATEGORY_INVALID_VALUE_RANGE)
        
        # System errors
        if 'permission' in error_str or 'access denied' in error_str:
            return (ErrorClassifier.ERROR_TYPE_SYSTEM, 
                   ErrorClassifier.CATEGORY_PERMISSION_DENIED)
        
        if any(keyword in error_str for keyword in [
            'internal error', 'system error', 'critical'
        ]):
            return (ErrorClassifier.ERROR_TYPE_SYSTEM, 
                   ErrorClassifier.CATEGORY_CODE_ERROR)
        
        # Unknown
        return (ErrorClassifier.ERROR_TYPE_SYSTEM, 
               ErrorClassifier.CATEGORY_UNKNOWN)
    
    @staticmethod
    def should_auto_recover(error_type: str, error_category: str, 
                          recovery_attempts: int = 0) -> bool:
        """
        Determine if message should be auto-recovered
        
        Args:
            error_type: Тип помилки
            error_category: Категорія помилки
            recovery_attempts: Кількість спроб відновлення
            
        Returns:
            True if should auto-recover
        """
        # Don't recover validation errors
        if error_type == ErrorClassifier.ERROR_TYPE_VALIDATION:
            return False
        
        # Don't recover system errors
        if error_type == ErrorClassifier.ERROR_TYPE_SYSTEM:
            return False
        
        # Recover transient errors if < 3 attempts
        if error_type == ErrorClassifier.ERROR_TYPE_TRANSIENT:
            return recovery_attempts < 3
        
        # Recover business errors if < 1 attempt
        if error_type == ErrorClassifier.ERROR_TYPE_BUSINESS:
            return recovery_attempts < 1
        
        return False


class MessageValidator:
    """Validator for IoT sensor messages"""
    
    REQUIRED_FIELDS = ['sensor_id', 'sensor_type', 'value', 
                      'latitude', 'longitude', 'timestamp']
    
    VALID_SENSOR_TYPES = ['temperature', 'humidity', 'light']
    
    VALUE_RANGES = {
        'temperature': (-50.0, 100.0),
        'humidity': (0.0, 100.0),
        'light': (0.0, 10000.0)
    }
    
    LOCATION_RANGES = {
        'latitude': (-90.0, 90.0),
        'longitude': (-180.0, 180.0)
    }
    
    @staticmethod
    def validate_message(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate sensor message
        
        Args:
            data: Дані повідомлення
            
        Returns:
            (is_valid, error_message)
        """
        # Check required fields
        missing_fields = [field for field in MessageValidator.REQUIRED_FIELDS 
                         if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Check sensor type
        sensor_type = data.get('sensor_type')
        if sensor_type not in MessageValidator.VALID_SENSOR_TYPES:
            return False, f"Invalid sensor_type: {sensor_type}. Must be one of: {', '.join(MessageValidator.VALID_SENSOR_TYPES)}"
        
        # Check value
        try:
            value = float(data['value'])
            min_val, max_val = MessageValidator.VALUE_RANGES[sensor_type]
            if not (min_val <= value <= max_val):
                return False, f"Value {value} is out of range [{min_val}, {max_val}] for {sensor_type}"
        except (ValueError, TypeError) as e:
            return False, f"Invalid value: {e}"
        
        # Check location
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
            
            lat_min, lat_max = MessageValidator.LOCATION_RANGES['latitude']
            lon_min, lon_max = MessageValidator.LOCATION_RANGES['longitude']
            
            if not (lat_min <= latitude <= lat_max):
                return False, f"Latitude {latitude} is out of range [{lat_min}, {lat_max}]"
            
            if not (lon_min <= longitude <= lon_max):
                return False, f"Longitude {longitude} is out of range [{lon_min}, {lon_max}]"
        except (ValueError, TypeError) as e:
            return False, f"Invalid location: {e}"
        
        # Check timestamp
        try:
            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            return False, f"Invalid timestamp: {e}"
        
        return True, None


class DLQLogger:
    """Logger for DLQ operations"""
    
    @staticmethod
    def log_dlq_message(message_id: str, error: Exception, 
                       original_message: str, delivery_count: int,
                       dead_letter_reason: Optional[str] = None,
                       dead_letter_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create structured log for DLQ message
        
        Returns:
            Dictionary with info to save to DB
        """
        error_type, error_category = ErrorClassifier.classify_error(error)
        
        # Extract sensor_id and sensor_type if possible
        sensor_id = None
        sensor_type = None
        try:
            data = json.loads(original_message)
            sensor_id = data.get('sensor_id')
            sensor_type = data.get('sensor_type')
        except:
            pass
        
        return {
            'message_id': message_id,
            'original_message': original_message,
            'sensor_id': sensor_id,
            'sensor_type': sensor_type,
            'error_type': error_type,
            'error_category': error_category,
            'error_message': str(error),
            'error_details': f"{type(error).__name__}: {str(error)}",
            'stack_trace': traceback.format_exc(),
            'delivery_count': delivery_count,
            'dead_letter_reason': dead_letter_reason,
            'dead_letter_error_description': dead_letter_description
        }
    
    @staticmethod
    def should_alert(error_type: str, error_category: str, 
                    delivery_count: int) -> Tuple[bool, str]:
        """
        Determine if alert should be sent
        
        Returns:
            (should_alert, alert_level) где alert_level: 'critical', 'warning', 'info'
        """
        # Critical alerts
        if error_type == ErrorClassifier.ERROR_TYPE_SYSTEM:
            return True, 'critical'
        
        if delivery_count >= 10:
            return True, 'critical'
        
        # Warning alerts
        if error_type == ErrorClassifier.ERROR_TYPE_BUSINESS:
            return True, 'warning'
        
        if delivery_count >= 5:
            return True, 'warning'
        
        return False, 'info'


class DLQMetrics:
    """Metrics collection for DLQ"""
    
    @staticmethod
    def calculate_recovery_priority(error_data: Dict[str, Any]) -> int:
        """
        Calculate recovery priority (higher = more important)
        
        Args:
            error_data: Дані помилки з БД
            
        Returns:
            Priority (0-100)
        """
        priority = 50  # Base priority
        
        error_type = error_data.get('error_type', '')
        error_category = error_data.get('error_category', '')
        delivery_count = error_data.get('delivery_count', 1)
        recovery_attempts = error_data.get('recovery_attempts', 0)
        
        # Transient errors - high priority
        if error_type == ErrorClassifier.ERROR_TYPE_TRANSIENT:
            priority += 30
        
        # Low delivery_count - higher priority
        if delivery_count <= 3:
            priority += 20
        elif delivery_count <= 6:
            priority += 10
        
        # Few recovery attempts - higher priority
        if recovery_attempts == 0:
            priority += 15
        elif recovery_attempts == 1:
            priority += 5
        
        # Validation errors - low priority
        if error_type == ErrorClassifier.ERROR_TYPE_VALIDATION:
            priority -= 20
        
        # System errors - require manual intervention
        if error_type == ErrorClassifier.ERROR_TYPE_SYSTEM:
            priority -= 30
        
        # Limit range
        priority = max(0, min(100, priority))
        
        return priority
    
    @staticmethod
    def format_time_in_dlq(dead_lettered_time: datetime) -> Dict[str, Any]:
        """
        Format time spent in DLQ
        
        Returns:
            Dictionary with various time representations
        """
        now = datetime.utcnow()
        delta = now - dead_lettered_time
        
        total_seconds = delta.total_seconds()
        minutes = int(total_seconds / 60)
        hours = int(minutes / 60)
        days = int(hours / 24)
        
        return {
            'total_seconds': int(total_seconds),
            'total_minutes': minutes,
            'total_hours': hours,
            'total_days': days,
            'formatted': f"{days}d {hours % 24}h {minutes % 60}m" if days > 0 
                        else f"{hours}h {minutes % 60}m" if hours > 0 
                        else f"{minutes}m"
        }


def create_alert_message(alert_type: str, error_data: Dict[str, Any], 
                        context: Optional[Dict[str, Any]] = None) -> str:
    """
    Create alert message
    
    Args:
        alert_type: Тип алерту
        error_data: Дані помилки
        context: Додатковий контекст
        
    Returns:
        Formatted message
    """
    if alert_type == 'high_volume':
        count = context.get('count', 0) if context else 0
        return f"⚠️ HIGH DLQ VOLUME: {count} messages in Dead Letter Queue"
    
    elif alert_type == 'system_error':
        sensor_id = error_data.get('sensor_id', 'unknown')
        error_msg = error_data.get('error_message', 'unknown error')
        return f"🚨 SYSTEM ERROR: {error_msg} (sensor: {sensor_id})"
    
    elif alert_type == 'recovery_failure':
        attempts = error_data.get('recovery_attempts', 0)
        sensor_id = error_data.get('sensor_id', 'unknown')
        return f"❌ RECOVERY FAILED: {attempts} failed attempts for sensor {sensor_id}"
    
    elif alert_type == 'prolonged_dlq':
        time_info = DLQMetrics.format_time_in_dlq(error_data['dead_lettered_time'])
        sensor_id = error_data.get('sensor_id', 'unknown')
        return f"⏱️ PROLONGED DLQ: Message from {sensor_id} in DLQ for {time_info['formatted']}"
    
    return f"Alert: {alert_type}"


# Export main classes and functions
__all__ = [
    'ErrorClassifier',
    'MessageValidator',
    'DLQLogger',
    'DLQMetrics',
    'create_alert_message'
]

