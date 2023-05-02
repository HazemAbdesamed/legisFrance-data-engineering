from airflow import DAG
from datetime import datetime
import time
from airflow.operators.python_operator import PythonOperator

from functions.scrape import scrape
from functions.load_to_db import load_data_to_db
from functions.visualization import create_visualizations
from functions.visualization import create_visualizations

from functions.monitoring import on_success_callback, on_failure_callback, start_time, end_time


default_args = {
    'owner' : 'Hazem',
    'start_date': datetime(2023, 4, 24),
    'retries': 0
}


dag_id = 'legifrance-data-eng'
with DAG(dag_id, default_args = default_args, schedule_interval='@weekly', catchup=False) as dag:
    
    t_start = PythonOperator(task_id="start", python_callable=start_time, provide_context=True, op_kwargs={'start_time': time.time()}, on_success_callback=on_success_callback, on_failure_callback=on_failure_callback) 

    t_fetch_data = PythonOperator(task_id="fetch-data", python_callable=scrape, on_success_callback=on_success_callback, on_failure_callback=on_failure_callback)
    
    t_load_data = PythonOperator(task_id="load-data", python_callable=load_data_to_db, on_success_callback=on_success_callback, on_failure_callback=on_failure_callback)
    
    t_create_visualizations = PythonOperator(task_id="create-visualizations", python_callable=create_visualizations, on_success_callback=on_success_callback, on_failure_callback=on_failure_callback)
    
    t_end = PythonOperator(task_id="end", python_callable=end_time, on_success_callback=on_success_callback,  on_failure_callback=on_failure_callback, provide_context=True) 


    t_start >> t_fetch_data >> t_load_data >> t_create_visualizations >> t_end

    