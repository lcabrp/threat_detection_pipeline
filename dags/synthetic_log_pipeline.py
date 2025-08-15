# dags/synthetic_log_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.append('/scripts')  # Add the scripts directory to the Python path

from log_generator import generate_logs

default_args = {
    'owner': 'leonardo',
    'start_date': datetime(2025, 8, 13),
    'retries': 1
}

with DAG(
    dag_id='synthetic_log_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['simulation', 'security']
) as dag:

    generate_synthetic_logs = PythonOperator(
        task_id='generate_synthetic_logs',
        python_callable=generate_logs,
        op_kwargs={'n': 50, 'output_file': 'data/generated_logs.json'}
    )

    generate_synthetic_logs