import json
import logging
import os
import sys
import azure.functions as func

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.db_helpers import get_dlq_statistics, get_db_connection


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP API to get Dead Letter Queue statistics
    
    Query parameters:
    - period: Time period ('1h', '24h', '7d', '30d', 'all', default: '24h')
    - error_type: Filter by error type (optional)
    - sensor_type: Filter by sensor type (optional)
    - detailed: If true, returns detailed info (default: false)
    """
    logging.info('Get DLQ statistics API called')
    
    try:
        # Get parameters
        period = req.params.get('period', '24h')
        error_type = req.params.get('error_type')
        sensor_type = req.params.get('sensor_type')
        detailed = req.params.get('detailed', 'false').lower() == 'true'
        
        # Validate period
        valid_periods = ['1h', '24h', '7d', '30d', 'all']
        if period not in valid_periods:
            return func.HttpResponse(
                json.dumps({
                    'error': f'Invalid period: {period}',
                    'valid_periods': valid_periods
                }, indent=2),
                status_code=400,
                mimetype='application/json'
            )
        
        # Get statistics from DB
        stats = get_dlq_statistics(period)
        
        if not stats:
            return func.HttpResponse(
                json.dumps({
                    'error': 'Failed to retrieve statistics',
                    'period': period
                }, indent=2),
                status_code=500,
                mimetype='application/json'
            )
        
        # Build response
        response = build_stats_response(stats, period, error_type, sensor_type, detailed)
        
        return func.HttpResponse(
            json.dumps(response, indent=2, default=str),
            status_code=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        logging.error(f"Error in get_dlq_stats: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            }, indent=2),
            status_code=500,
            mimetype='application/json'
        )


def build_stats_response(stats, period, error_type_filter, sensor_type_filter, detailed):
    """
    Build response with statistics
    """
    overview = stats.get('overview', {})
    top_errors = stats.get('top_errors', [])
    top_sensors = stats.get('top_problematic_sensors', [])
    
    # Basic statistics
    total_errors = overview.get('total_errors', 0)
    recovered_count = overview.get('recovered_count', 0)
    pending_count = overview.get('pending_count', 0)
    
    response = {
        'period': period,
        'summary': {
            'total_errors': total_errors,
            'recovered': recovered_count,
            'pending': pending_count,
            'failed': overview.get('failed_count', 0),
            'recovery_rate': round((recovered_count / total_errors * 100) if total_errors > 0 else 0, 2),
            'avg_resolution_time_minutes': overview.get('avg_resolution_time_minutes')
        },
        'errors_by_type': {
            'transient': overview.get('transient_errors', 0),
            'validation': overview.get('validation_errors', 0),
            'business': overview.get('business_errors', 0),
            'system': overview.get('system_errors', 0)
        },
        'time_range': {
            'first_error': str(overview.get('first_error_time')) if overview.get('first_error_time') else None,
            'last_error': str(overview.get('last_error_time')) if overview.get('last_error_time') else None
        }
    }
    
    # Filter by error_type
    if error_type_filter:
        top_errors = [e for e in top_errors if e.get('error_type') == error_type_filter]
    
    # Filter by sensor_type
    if sensor_type_filter:
        top_sensors = [s for s in top_sensors if s.get('sensor_type') == sensor_type_filter]
    
    # Top errors
    if top_errors:
        response['top_errors'] = []
        for error in top_errors[:10]:  # Top 10
            response['top_errors'].append({
                'category': error.get('error_category'),
                'type': error.get('error_type'),
                'count': error.get('error_count'),
                'last_occurrence': str(error.get('last_occurrence'))
            })
    
    # Top problematic sensors
    if top_sensors:
        response['problematic_sensors'] = []
        for sensor in top_sensors[:10]:  # Top 10
            response['problematic_sensors'].append({
                'sensor_id': sensor.get('sensor_id'),
                'sensor_type': sensor.get('sensor_type'),
                'error_count': sensor.get('error_count'),
                'last_error': str(sensor.get('last_error'))
            })
    
    # Detailed information
    if detailed:
        response['detailed'] = get_detailed_stats(period, error_type_filter, sensor_type_filter)
    
    # Recommendations
    response['recommendations'] = generate_recommendations(response)
    
    return response


def get_detailed_stats(period, error_type_filter, sensor_type_filter):
    """
    Get detailed statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(as_dict=True)
        
        try:
            # Determine cutoff time
            cutoff_query = ""
            if period == '1h':
                cutoff_query = "AND dead_lettered_time >= DATEADD(HOUR, -1, GETUTCDATE())"
            elif period == '24h':
                cutoff_query = "AND dead_lettered_time >= DATEADD(HOUR, -24, GETUTCDATE())"
            elif period == '7d':
                cutoff_query = "AND dead_lettered_time >= DATEADD(DAY, -7, GETUTCDATE())"
            elif period == '30d':
                cutoff_query = "AND dead_lettered_time >= DATEADD(DAY, -30, GETUTCDATE())"
            
            # Filters
            filters = []
            if error_type_filter:
                filters.append(f"error_type = '{error_type_filter}'")
            if sensor_type_filter:
                filters.append(f"sensor_type = '{sensor_type_filter}'")
            
            filter_query = " AND " + " AND ".join(filters) if filters else ""
            
            # Errors over time (hourly breakdown)
            cursor.execute(f"""
                SELECT 
                    DATEPART(HOUR, dead_lettered_time) as hour,
                    COUNT(*) as count,
                    error_type
                FROM dlq_errors
                WHERE 1=1 {cutoff_query} {filter_query}
                GROUP BY DATEPART(HOUR, dead_lettered_time), error_type
                ORDER BY hour
            """)
            
            hourly_distribution = cursor.fetchall()
            
            # Distribution by status
            cursor.execute(f"""
                SELECT 
                    status,
                    COUNT(*) as count
                FROM dlq_errors
                WHERE 1=1 {cutoff_query} {filter_query}
                GROUP BY status
            """)
            
            status_distribution = cursor.fetchall()
            
            # Average time in DLQ
            cursor.execute(f"""
                SELECT 
                    error_type,
                    AVG(DATEDIFF(MINUTE, dead_lettered_time, COALESCE(resolved_time, GETUTCDATE()))) as avg_time_in_dlq_minutes,
                    MIN(DATEDIFF(MINUTE, dead_lettered_time, COALESCE(resolved_time, GETUTCDATE()))) as min_time_in_dlq_minutes,
                    MAX(DATEDIFF(MINUTE, dead_lettered_time, COALESCE(resolved_time, GETUTCDATE()))) as max_time_in_dlq_minutes
                FROM dlq_errors
                WHERE 1=1 {cutoff_query} {filter_query}
                GROUP BY error_type
            """)
            
            time_in_dlq = cursor.fetchall()
            
            # Recovery attempts distribution
            cursor.execute(f"""
                SELECT 
                    recovery_attempts,
                    COUNT(*) as count
                FROM dlq_errors
                WHERE 1=1 {cutoff_query} {filter_query}
                GROUP BY recovery_attempts
                ORDER BY recovery_attempts
            """)
            
            recovery_attempts_dist = cursor.fetchall()
            
            return {
                'hourly_distribution': [dict(row) for row in hourly_distribution],
                'status_distribution': [dict(row) for row in status_distribution],
                'time_in_dlq': [dict(row) for row in time_in_dlq],
                'recovery_attempts_distribution': [dict(row) for row in recovery_attempts_dist]
            }
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Error getting detailed stats: {str(e)}")
        return None


def generate_recommendations(stats_response):
    """
    Generate recommendations based on statistics
    """
    recommendations = []
    
    summary = stats_response.get('summary', {})
    errors_by_type = stats_response.get('errors_by_type', {})
    
    total_errors = summary.get('total_errors', 0)
    recovery_rate = summary.get('recovery_rate', 0)
    
    # High error level
    if total_errors > 100:
        recommendations.append({
            'severity': 'high',
            'category': 'volume',
            'message': f'High volume of DLQ messages ({total_errors}). Investigation recommended.',
            'action': 'Review error patterns and check system health'
        })
    elif total_errors > 50:
        recommendations.append({
            'severity': 'medium',
            'category': 'volume',
            'message': f'Moderate volume of DLQ messages ({total_errors}).',
            'action': 'Monitor trends and consider preventive measures'
        })
    
    # Low recovery rate
    if recovery_rate < 50 and total_errors > 10:
        recommendations.append({
            'severity': 'high',
            'category': 'recovery',
            'message': f'Low recovery rate ({recovery_rate}%).',
            'action': 'Review why messages are not being recovered and fix root causes'
        })
    
    # Many validation errors
    validation_pct = (errors_by_type.get('validation', 0) / total_errors * 100) if total_errors > 0 else 0
    if validation_pct > 30:
        recommendations.append({
            'severity': 'medium',
            'category': 'validation',
            'message': f'High percentage of validation errors ({validation_pct:.1f}%).',
            'action': 'Improve data validation at the source (IoT emulator/sensors)'
        })
    
    # Many system errors
    system_pct = (errors_by_type.get('system', 0) / total_errors * 100) if total_errors > 0 else 0
    if system_pct > 10:
        recommendations.append({
            'severity': 'critical',
            'category': 'system',
            'message': f'System errors detected ({system_pct:.1f}%).',
            'action': 'Immediate attention required - check application logs and fix bugs'
        })
    
    # Many transient errors
    transient_pct = (errors_by_type.get('transient', 0) / total_errors * 100) if total_errors > 0 else 0
    if transient_pct > 50:
        recommendations.append({
            'severity': 'medium',
            'category': 'infrastructure',
            'message': f'High percentage of transient errors ({transient_pct:.1f}%).',
            'action': 'Check database and network connectivity, consider scaling resources'
        })
    
    # Problematic sensors
    problematic_sensors = stats_response.get('problematic_sensors', [])
    if len(problematic_sensors) > 0:
        top_sensor = problematic_sensors[0]
        if top_sensor['error_count'] > 10:
            recommendations.append({
                'severity': 'medium',
                'category': 'sensor',
                'message': f"Sensor {top_sensor['sensor_id']} has {top_sensor['error_count']} errors.",
                'action': f"Investigate sensor {top_sensor['sensor_id']} - may need recalibration or replacement"
            })
    
    # If no problems
    if not recommendations:
        recommendations.append({
            'severity': 'info',
            'category': 'health',
            'message': 'DLQ health looks good!',
            'action': 'Continue monitoring'
        })
    
    return recommendations

