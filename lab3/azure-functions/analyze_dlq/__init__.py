import json
import logging
import os
import sys
from datetime import datetime, timedelta
import azure.functions as func

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.db_helpers import get_db_connection, create_alert, update_dlq_statistics_hourly
from shared.dlq_helpers import create_alert_message


def main(mytimer: func.TimerRequest) -> None:
    """
    Periodic DLQ analysis (runs hourly)
    
    Performs:
    1. Update DLQ statistics
    2. Check threshold values
    3. Create alerts if needed
    4. Identify error patterns
    """
    utc_timestamp = datetime.utcnow().replace(tzinfo=None).isoformat()
    
    if mytimer.past_due:
        logging.info('The timer is past due!')
    
    logging.info(f'DLQ Analysis function started at {utc_timestamp}')
    
    try:
        # 1. Update hourly statistics
        logging.info('Updating hourly statistics...')
        update_dlq_statistics_hourly()
        
        # 2. Analyze current DLQ state
        analysis_results = analyze_dlq_state()
        
        # 3. Check thresholds and create alerts
        check_thresholds_and_alert(analysis_results)
        
        # 4. Identify patterns
        patterns = identify_error_patterns()
        if patterns:
            logging.info(f"Identified {len(patterns)} error patterns")
            for pattern in patterns:
                logging.info(f"  Pattern: {pattern['description']}")
        
        # 5. Generate summary
        summary = generate_analysis_summary(analysis_results, patterns)
        logging.info(f"Analysis completed. Summary: {json.dumps(summary, indent=2)}")
        
    except Exception as e:
        logging.error(f"Error in analyze_dlq function: {str(e)}", exc_info=True)


def analyze_dlq_state():
    """
    Analyze current DLQ state
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(as_dict=True)
        
        try:
            # Overall statistics for last hour
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_errors_last_hour,
                    SUM(CASE WHEN error_type = 'transient' THEN 1 ELSE 0 END) as transient_errors,
                    SUM(CASE WHEN error_type = 'validation' THEN 1 ELSE 0 END) as validation_errors,
                    SUM(CASE WHEN error_type = 'business' THEN 1 ELSE 0 END) as business_errors,
                    SUM(CASE WHEN error_type = 'system' THEN 1 ELSE 0 END) as system_errors
                FROM dlq_errors
                WHERE dead_lettered_time >= DATEADD(HOUR, -1, GETUTCDATE())
            """)
            
            hourly_stats = cursor.fetchone()
            
            # Pending errors statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_pending,
                    AVG(DATEDIFF(MINUTE, dead_lettered_time, GETUTCDATE())) as avg_age_minutes,
                    MAX(DATEDIFF(MINUTE, dead_lettered_time, GETUTCDATE())) as max_age_minutes
                FROM dlq_errors
                WHERE status = 'pending'
            """)
            
            pending_stats = cursor.fetchone()
            
            # Failed recoveries statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as failed_recoveries_last_hour
                FROM dlq_recovery
                WHERE recovery_status = 'failed'
                    AND recovery_time >= DATEADD(HOUR, -1, GETUTCDATE())
            """)
            
            recovery_stats = cursor.fetchone()
            
            # Trending - compare with previous hour
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_errors_prev_hour
                FROM dlq_errors
                WHERE dead_lettered_time >= DATEADD(HOUR, -2, GETUTCDATE())
                    AND dead_lettered_time < DATEADD(HOUR, -1, GETUTCDATE())
            """)
            
            prev_hour_stats = cursor.fetchone()
            
            return {
                'hourly': dict(hourly_stats),
                'pending': dict(pending_stats),
                'recovery': dict(recovery_stats),
                'trend': dict(prev_hour_stats),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Error analyzing DLQ state: {str(e)}")
        return None


def check_thresholds_and_alert(analysis_results):
    """
    Check threshold values and create alerts
    """
    if not analysis_results:
        return
    
    hourly = analysis_results['hourly']
    pending = analysis_results['pending']
    recovery = analysis_results['recovery']
    
    alerts_created = []
    
    # Alert 1: High error volume per hour
    errors_last_hour = hourly.get('total_errors_last_hour', 0)
    if errors_last_hour > 50:
        alert_data = {
            'alert_type': 'critical',
            'alert_category': 'high_volume',
            'alert_message': f'⚠️ HIGH DLQ VOLUME: {errors_last_hour} messages in last hour',
            'alert_details': json.dumps(hourly),
            'affected_count': errors_last_hour,
            'threshold_value': 50,
            'current_value': errors_last_hour
        }
        if create_alert(alert_data):
            alerts_created.append('high_volume')
            logging.warning(f"ALERT: High DLQ volume - {errors_last_hour} messages")
    
    # Alert 2: System errors
    system_errors = hourly.get('system_errors', 0)
    if system_errors > 0:
        alert_data = {
            'alert_type': 'critical',
            'alert_category': 'system_errors',
            'alert_message': f'🚨 SYSTEM ERRORS DETECTED: {system_errors} system errors in last hour',
            'alert_details': json.dumps({'system_errors': system_errors}),
            'affected_count': system_errors,
            'threshold_value': 0,
            'current_value': system_errors
        }
        if create_alert(alert_data):
            alerts_created.append('system_errors')
            logging.critical(f"ALERT: System errors detected - {system_errors} errors")
    
    # Alert 3: Many pending messages
    total_pending = pending.get('total_pending', 0)
    if total_pending > 100:
        alert_data = {
            'alert_type': 'warning',
            'alert_category': 'high_pending',
            'alert_message': f'⚠️ HIGH PENDING COUNT: {total_pending} pending messages in DLQ',
            'alert_details': json.dumps(pending),
            'affected_count': total_pending,
            'threshold_value': 100,
            'current_value': total_pending
        }
        if create_alert(alert_data):
            alerts_created.append('high_pending')
            logging.warning(f"ALERT: High pending count - {total_pending} messages")
    
    # Alert 4: Old messages in DLQ
    max_age = pending.get('max_age_minutes', 0)
    if max_age > 1440:  # 24 hours
        alert_data = {
            'alert_type': 'warning',
            'alert_category': 'prolonged_dlq',
            'alert_message': f'⏱️ PROLONGED DLQ: Messages older than 24 hours ({max_age} minutes)',
            'alert_details': json.dumps(pending),
            'affected_count': 1,
            'threshold_value': 1440,
            'current_value': max_age
        }
        if create_alert(alert_data):
            alerts_created.append('prolonged_dlq')
            logging.warning(f"ALERT: Prolonged DLQ - oldest message: {max_age} minutes")
    
    # Alert 5: Many failed recovery attempts
    failed_recoveries = recovery.get('failed_recoveries_last_hour', 0)
    if failed_recoveries > 10:
        alert_data = {
            'alert_type': 'warning',
            'alert_category': 'recovery_failures',
            'alert_message': f'❌ HIGH RECOVERY FAILURE RATE: {failed_recoveries} failed recoveries in last hour',
            'alert_details': json.dumps(recovery),
            'affected_count': failed_recoveries,
            'threshold_value': 10,
            'current_value': failed_recoveries
        }
        if create_alert(alert_data):
            alerts_created.append('recovery_failures')
            logging.warning(f"ALERT: High recovery failure rate - {failed_recoveries} failures")
    
    # Alert 6: Rapid error growth
    prev_hour = analysis_results['trend'].get('total_errors_prev_hour', 0)
    if prev_hour > 0:
        growth_rate = ((errors_last_hour - prev_hour) / prev_hour) * 100
        if growth_rate > 200:  # More than 200% growth
            alert_data = {
                'alert_type': 'critical',
                'alert_category': 'rapid_growth',
                'alert_message': f'📈 RAPID ERROR GROWTH: {growth_rate:.1f}% increase in last hour',
                'alert_details': json.dumps({
                    'current_hour': errors_last_hour,
                    'previous_hour': prev_hour,
                    'growth_rate': growth_rate
                }),
                'affected_count': errors_last_hour,
                'threshold_value': 200,
                'current_value': growth_rate
            }
            if create_alert(alert_data):
                alerts_created.append('rapid_growth')
                logging.critical(f"ALERT: Rapid error growth - {growth_rate:.1f}% increase")
    
    logging.info(f"Alerts created: {len(alerts_created)} - {', '.join(alerts_created)}")


def identify_error_patterns():
    """
    Identify error patterns
    """
    patterns = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(as_dict=True)
        
        try:
            # Pattern 1: Repeated errors for one sensor
            cursor.execute("""
                SELECT 
                    sensor_id,
                    sensor_type,
                    error_category,
                    COUNT(*) as error_count
                FROM dlq_errors
                WHERE dead_lettered_time >= DATEADD(HOUR, -24, GETUTCDATE())
                    AND sensor_id IS NOT NULL
                GROUP BY sensor_id, sensor_type, error_category
                HAVING COUNT(*) >= 5
                ORDER BY error_count DESC
            """)
            
            repeated_errors = cursor.fetchall()
            for error in repeated_errors:
                patterns.append({
                    'type': 'repeated_sensor_error',
                    'description': f"Sensor {error['sensor_id']} has {error['error_count']} errors of type {error['error_category']}",
                    'severity': 'high' if error['error_count'] > 10 else 'medium',
                    'data': dict(error)
                })
            
            # Pattern 2: Error spikes (many errors in short time)
            cursor.execute("""
                SELECT 
                    DATEPART(HOUR, dead_lettered_time) as hour,
                    COUNT(*) as error_count,
                    error_type
                FROM dlq_errors
                WHERE dead_lettered_time >= DATEADD(HOUR, -24, GETUTCDATE())
                GROUP BY DATEPART(HOUR, dead_lettered_time), error_type
                HAVING COUNT(*) > 20
                ORDER BY error_count DESC
            """)
            
            spikes = cursor.fetchall()
            for spike in spikes:
                patterns.append({
                    'type': 'error_spike',
                    'description': f"{spike['error_count']} {spike['error_type']} errors at hour {spike['hour']}",
                    'severity': 'high',
                    'data': dict(spike)
                })
            
            # Pattern 3: New error types
            cursor.execute("""
                SELECT DISTINCT 
                    error_category,
                    error_type,
                    MIN(dead_lettered_time) as first_occurrence
                FROM dlq_errors
                WHERE dead_lettered_time >= DATEADD(HOUR, -1, GETUTCDATE())
                    AND error_category NOT IN (
                        SELECT DISTINCT error_category
                        FROM dlq_errors
                        WHERE dead_lettered_time >= DATEADD(HOUR, -25, GETUTCDATE())
                            AND dead_lettered_time < DATEADD(HOUR, -1, GETUTCDATE())
                    )
            """)
            
            new_errors = cursor.fetchall()
            for error in new_errors:
                patterns.append({
                    'type': 'new_error_type',
                    'description': f"New error type detected: {error['error_type']} - {error['error_category']}",
                    'severity': 'medium',
                    'data': dict(error)
                })
            
            return patterns
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Error identifying patterns: {str(e)}")
        return []


def generate_analysis_summary(analysis_results, patterns):
    """
    Generate analysis summary
    """
    if not analysis_results:
        return {'status': 'error', 'message': 'Analysis failed'}
    
    hourly = analysis_results['hourly']
    pending = analysis_results['pending']
    
    return {
        'timestamp': analysis_results['timestamp'],
        'errors_last_hour': hourly.get('total_errors_last_hour', 0),
        'pending_count': pending.get('total_pending', 0),
        'avg_age_minutes': pending.get('avg_age_minutes', 0),
        'patterns_identified': len(patterns),
        'health_status': determine_health_status(hourly, pending),
        'requires_attention': requires_immediate_attention(hourly, pending)
    }


def determine_health_status(hourly, pending):
    """
    Determine DLQ health status
    """
    errors_last_hour = hourly.get('total_errors_last_hour', 0)
    system_errors = hourly.get('system_errors', 0)
    pending_count = pending.get('total_pending', 0)
    
    if system_errors > 0 or errors_last_hour > 50:
        return 'critical'
    elif pending_count > 100 or errors_last_hour > 20:
        return 'warning'
    elif errors_last_hour > 0 or pending_count > 0:
        return 'degraded'
    else:
        return 'healthy'


def requires_immediate_attention(hourly, pending):
    """
    Determine if immediate attention required
    """
    system_errors = hourly.get('system_errors', 0)
    errors_last_hour = hourly.get('total_errors_last_hour', 0)
    max_age = pending.get('max_age_minutes', 0)
    
    return system_errors > 0 or errors_last_hour > 50 or max_age > 1440

