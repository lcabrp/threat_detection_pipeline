from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.transform_logs import transform_logs
from scripts.load_to_splunk import load_to_splunk

from scripts.etl_to_sqlite import etl_to_sqlite

etl_task = PythonOperator(
    task_id='etl_to_sqlite',
    python_callable=etl_to_sqlite,
    op_kwargs={
        'json_path': 'data/generated_logs.json',
        'db_path': 'db/threat_logs.db'
    }
)

generate_synthetic_logs >> etl_task

def extract_wrapper():
    """
    Calls extract_logs from scripts.extract_logs to extract logs from log files to a JSON file.

    Returns:
        None
    """
    from scripts.extract_logs import extract_logs
    extract_logs()

with DAG("threat_etl_pipeline", start_date=datetime(2025, 8, 13), schedule_interval="@daily", catchup=False) as dag:
    extract = PythonOperator(task_id="extract_logs", python_callable=extract_wrapper)
    transform = PythonOperator(task_id="transform_logs", python_callable=transform_logs)
    load = PythonOperator(task_id="load_to_splunk", python_callable=load_to_splunk)

    extract >> transform >> load