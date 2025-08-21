"""
Cybersecurity Data Engineering Learning DAG
============================================

This DAG introduces core Data Engineering concepts:
- Data partitioning (daily batch processing)
- Data quality validation
- Multi-layer architecture (Bronze/Silver/Gold)
- Error handling and monitoring
- Incremental processing patterns

Learning Focus: Airflow basics, data validation, pipeline patterns
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import pandas as pd
import json
import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'data-engineer-student',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'cybersec_learning_pipeline',
    default_args=default_args,
    description='Learning Data Engineering with Cybersecurity Data',
    schedule_interval=timedelta(days=1),  # Run daily
    catchup=False,  # Don't run for past dates
    max_active_runs=1,  # Only one instance at a time
    tags=['learning', 'cybersecurity', 'data-engineering'],
)

def setup_directories(**context):
    """
    Data Engineering Concept: Environment Preparation
    
    Sets up the directory structure for data lake architecture:
    - Bronze layer: Raw data as-is
    - Silver layer: Cleaned and validated data  
    - Gold layer: Business-ready analytics
    """
    base_path = Path("/app")
    
    directories = [
        "data/bronze/logs",
        "data/silver/validated_logs", 
        "data/gold/daily_summaries",
        "data/gold/threat_reports"
    ]
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {dir_path}")
    
    return "Directory setup completed"

def generate_daily_logs(**context):
    """
    Data Engineering Concept: Data Generation/Ingestion
    
    Generates synthetic cybersecurity logs for a specific date.
    In real scenarios, this would be data ingestion from:
    - APIs, databases, file systems, message queues
    
    Key concepts demonstrated:
    - Date-based partitioning
    - Deterministic data generation (for testing)
    - Data volume management
    """
    import random
    import numpy as np
    from datetime import datetime, timedelta
    
    # Get execution date from Airflow context
    execution_date = context['ds']  # Format: YYYY-MM-DD
    logger.info(f"Generating logs for date: {execution_date}")
    
    # Set seed for reproducible data (important for testing)
    random.seed(hash(execution_date))
    np.random.seed(hash(execution_date) % (2**32))
    
    # Generate realistic log volume (varies by day of week)
    date_obj = datetime.strptime(execution_date, '%Y-%m-%d')
    is_weekend = date_obj.weekday() >= 5
    base_volume = 30000 if not is_weekend else 15000
    daily_volume = base_volume + random.randint(-5000, 5000)
    
    logger.info(f"Generating {daily_volume} log events")
    
    # Event types with realistic probabilities
    event_types = [
        "login_success", "login_failed", "file_access", "network_scan",
        "malware_detected", "suspicious_activity", "data_transfer", "system_error"
    ]
    event_probabilities = [0.25, 0.15, 0.20, 0.08, 0.05, 0.07, 0.15, 0.05]
    
    # Generate logs
    logs = []
    for i in range(daily_volume):
        # Create realistic timestamp within the day
        hour = np.random.choice(range(24), p=[
            0.02, 0.01, 0.01, 0.01, 0.01, 0.02,  # 00-05: Very low activity
            0.03, 0.05, 0.08, 0.09, 0.08, 0.07,  # 06-11: Rising activity
            0.06, 0.07, 0.08, 0.09, 0.08, 0.07,  # 12-17: Peak business hours
            0.06, 0.05, 0.04, 0.03, 0.02, 0.02   # 18-23: Declining activity
        ])
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        # Create log entry
        log_entry = {
            "timestamp": f"{execution_date}T{hour:02d}:{minute:02d}:{second:02d}Z",
            "event_id": f"evt_{execution_date.replace('-', '')}_{i:06d}",
            "event_type": np.random.choice(event_types, p=event_probabilities),
            "source_ip": f"192.168.{random.randint(1, 10)}.{random.randint(1, 254)}",
            "destination_ip": f"10.0.{random.randint(1, 5)}.{random.randint(1, 254)}",
            "user": f"user{random.randint(1, 50)}",
            "severity": np.random.choice(["low", "medium", "high", "critical"], 
                                       p=[0.5, 0.3, 0.15, 0.05]),
            "bytes_transferred": random.randint(100, 1000000),
            "response_time_ms": max(1, int(np.random.gamma(2, 50))),
            "risk_score": round(random.uniform(0, 100), 2)
        }
        logs.append(log_entry)
    
    # Save to Bronze layer (raw data)
    output_path = f"/app/data/bronze/logs/date={execution_date}/logs.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for log in logs:
            f.write(json.dumps(log) + '\n')  # NDJSON format
    
    logger.info(f"Generated {len(logs)} logs saved to {output_path}")
    return {"logs_generated": len(logs), "file_path": output_path}

def validate_data_quality(**context):
    """
    Data Engineering Concept: Data Quality Validation
    
    Critical step in any data pipeline:
    - Completeness checks
    - Consistency validation
    - Business rule verification
    
    In production, you'd use tools like Great Expectations
    """
    execution_date = context['ds']
    input_path = f"/app/data/bronze/logs/date={execution_date}/logs.json"
    
    logger.info(f"Validating data quality for {execution_date}")
    
    # Load data for validation
    logs = []
    with open(input_path, 'r') as f:
        for line in f:
            logs.append(json.loads(line.strip()))
    
    # Data quality checks
    quality_metrics = {
        "total_records": len(logs),
        "null_timestamps": 0,
        "invalid_ips": 0,
        "missing_users": 0,
        "severity_distribution": {},
        "risk_score_stats": {}
    }
    
    for log in logs:
        # Check for null timestamps
        if not log.get('timestamp'):
            quality_metrics["null_timestamps"] += 1
        
        # Validate IP format (basic check)
        source_ip = log.get('source_ip', '')
        if not source_ip or len(source_ip.split('.')) != 4:
            quality_metrics["invalid_ips"] += 1
        
        # Check for missing users
        if not log.get('user'):
            quality_metrics["missing_users"] += 1
        
        # Severity distribution
        severity = log.get('severity', 'unknown')
        quality_metrics["severity_distribution"][severity] = \
            quality_metrics["severity_distribution"].get(severity, 0) + 1
    
    # Calculate risk score statistics
    risk_scores = [log.get('risk_score', 0) for log in logs if log.get('risk_score')]
    if risk_scores:
        quality_metrics["risk_score_stats"] = {
            "mean": sum(risk_scores) / len(risk_scores),
            "min": min(risk_scores),
            "max": max(risk_scores)
        }
    
    # Data quality thresholds (configurable in production)
    quality_pass = (
        quality_metrics["null_timestamps"] < len(logs) * 0.01 and  # <1% null timestamps
        quality_metrics["invalid_ips"] < len(logs) * 0.05 and      # <5% invalid IPs
        quality_metrics["missing_users"] < len(logs) * 0.02        # <2% missing users
    )
    
    # Save quality report
    quality_report = {
        "date": execution_date,
        "metrics": quality_metrics,
        "quality_passed": quality_pass,
        "timestamp": datetime.now().isoformat()
    }
    
    report_path = f"/app/data/silver/quality_reports/date={execution_date}_report.json"
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(quality_report, f, indent=2)
    
    logger.info(f"Data quality check {'PASSED' if quality_pass else 'FAILED'}")
    logger.info(f"Quality report saved to {report_path}")
    
    if not quality_pass:
        raise ValueError(f"Data quality checks failed for {execution_date}")
    
    return quality_report

def transform_to_silver(**context):
    """
    Data Engineering Concept: Data Transformation (Bronze -> Silver)
    
    Cleans and structures data for analysis:
    - Standardizes formats
    - Enriches with additional fields
    - Filters out invalid records
    - Applies business rules
    """
    execution_date = context['ds']
    input_path = f"/app/data/bronze/logs/date={execution_date}/logs.json"
    output_path = f"/app/data/silver/validated_logs/date={execution_date}/cleaned_logs.json"
    
    logger.info(f"Transforming data to Silver layer for {execution_date}")
    
    # Load bronze data
    logs = []
    with open(input_path, 'r') as f:
        for line in f:
            logs.append(json.loads(line.strip()))
    
    # Transform and enrich data
    transformed_logs = []
    for log in logs:
        # Skip invalid records
        if not log.get('timestamp') or not log.get('source_ip'):
            continue
        
        # Enrich with additional fields
        transformed_log = log.copy()
        
        # Add derived fields
        transformed_log['is_suspicious'] = (
            log.get('severity') in ['high', 'critical'] or
            log.get('risk_score', 0) > 70 or
            log.get('event_type') in ['malware_detected', 'suspicious_activity']
        )
        
        # Categorize risk level
        risk_score = log.get('risk_score', 0)
        if risk_score >= 80:
            transformed_log['risk_category'] = 'critical'
        elif risk_score >= 60:
            transformed_log['risk_category'] = 'high'
        elif risk_score >= 30:
            transformed_log['risk_category'] = 'medium'
        else:
            transformed_log['risk_category'] = 'low'
        
        # Add processing metadata
        transformed_log['processed_at'] = datetime.now().isoformat()
        transformed_log['pipeline_version'] = '1.0'
        
        transformed_logs.append(transformed_log)
    
    # Save to Silver layer
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for log in transformed_logs:
            f.write(json.dumps(log) + '\n')
    
    logger.info(f"Transformed {len(transformed_logs)} records to Silver layer")
    return {"records_transformed": len(transformed_logs), "output_path": output_path}

def create_gold_analytics(**context):
    """
    Data Engineering Concept: Analytics Layer (Silver -> Gold)
    
    Creates business-ready insights and aggregations:
    - Daily summaries
    - Threat intelligence
    - KPI calculations
    - Trend analysis
    """
    execution_date = context['ds']
    input_path = f"/app/data/silver/validated_logs/date={execution_date}/cleaned_logs.json"
    
    logger.info(f"Creating Gold layer analytics for {execution_date}")
    
    # Load silver data
    logs = []
    with open(input_path, 'r') as f:
        for line in f:
            logs.append(json.loads(line.strip()))
    
    # Create daily summary
    daily_summary = {
        "date": execution_date,
        "total_events": len(logs),
        "suspicious_events": sum(1 for log in logs if log.get('is_suspicious')),
        "unique_users": len(set(log.get('user') for log in logs if log.get('user'))),
        "unique_source_ips": len(set(log.get('source_ip') for log in logs if log.get('source_ip'))),
        "event_type_distribution": {},
        "severity_distribution": {},
        "risk_category_distribution": {},
        "top_users_by_activity": {},
        "top_source_ips": {},
        "hourly_activity": [0] * 24
    }
    
    # Calculate distributions and top lists
    for log in logs:
        # Event type distribution
        event_type = log.get('event_type', 'unknown')
        daily_summary["event_type_distribution"][event_type] = \
            daily_summary["event_type_distribution"].get(event_type, 0) + 1
        
        # Severity distribution  
        severity = log.get('severity', 'unknown')
        daily_summary["severity_distribution"][severity] = \
            daily_summary["severity_distribution"].get(severity, 0) + 1
        
        # Risk category distribution
        risk_category = log.get('risk_category', 'unknown')
        daily_summary["risk_category_distribution"][risk_category] = \
            daily_summary["risk_category_distribution"].get(risk_category, 0) + 1
        
        # Top users by activity
        user = log.get('user')
        if user:
            daily_summary["top_users_by_activity"][user] = \
                daily_summary["top_users_by_activity"].get(user, 0) + 1
        
        # Top source IPs
        source_ip = log.get('source_ip')
        if source_ip:
            daily_summary["top_source_ips"][source_ip] = \
                daily_summary["top_source_ips"].get(source_ip, 0) + 1
        
        # Hourly activity
        timestamp = log.get('timestamp', '')
        if 'T' in timestamp:
            hour = int(timestamp.split('T')[1].split(':')[0])
            daily_summary["hourly_activity"][hour] += 1
    
    # Sort top lists and keep top 10
    daily_summary["top_users_by_activity"] = dict(
        sorted(daily_summary["top_users_by_activity"].items(), 
               key=lambda x: x[1], reverse=True)[:10]
    )
    
    daily_summary["top_source_ips"] = dict(
        sorted(daily_summary["top_source_ips"].items(), 
               key=lambda x: x[1], reverse=True)[:10]
    )
    
    # Calculate KPIs
    total_events = daily_summary["total_events"]
    daily_summary["kpis"] = {
        "suspicious_event_rate": round(daily_summary["suspicious_events"] / total_events * 100, 2) if total_events > 0 else 0,
        "critical_risk_rate": round(daily_summary["risk_category_distribution"].get("critical", 0) / total_events * 100, 2) if total_events > 0 else 0,
        "unique_user_ratio": round(daily_summary["unique_users"] / total_events * 100, 2) if total_events > 0 else 0,
        "peak_hour": daily_summary["hourly_activity"].index(max(daily_summary["hourly_activity"])),
        "peak_hour_events": max(daily_summary["hourly_activity"])
    }
    
    # Save daily summary to Gold layer
    summary_path = f"/app/data/gold/daily_summaries/date={execution_date}_summary.json"
    Path(summary_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(summary_path, 'w') as f:
        json.dump(daily_summary, f, indent=2)
    
    logger.info(f"Created daily summary with {total_events} events analyzed")
    return daily_summary

# Define the task dependencies
setup_task = PythonOperator(
    task_id='setup_directories',
    python_callable=setup_directories,
    dag=dag,
)

generate_task = PythonOperator(
    task_id='generate_daily_logs',
    python_callable=generate_daily_logs,
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_data_quality', 
    python_callable=validate_data_quality,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_to_silver',
    python_callable=transform_to_silver,
    dag=dag,
)

analytics_task = PythonOperator(
    task_id='create_gold_analytics',
    python_callable=create_gold_analytics,
    dag=dag,
)

# Set up the task dependencies (pipeline flow)
setup_task >> generate_task >> validate_task >> transform_task >> analytics_task