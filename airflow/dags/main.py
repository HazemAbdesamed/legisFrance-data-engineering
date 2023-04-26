from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator

from functions.scrape import scrape
from functions.load_to_db import load_data_to_db



default_args = {
    'owner' : 'Hazem',
    'start_date': datetime(2023, 4, 24),
    'retries': 0
}

with DAG('legifrance-data-eng', default_args = default_args, schedule_interval='@weekly', template_searchpath=['/usr/local/airflow/db_data_airflow/'], catchup=False) as dag:

    t_fetch_data = PythonOperator(task_id="fetch-data", python_callable=scrape)
    t_load_data = PythonOperator(task_id="load-data", python_callable=load_data_to_db)

    t_fetch_data >> t_load_data    