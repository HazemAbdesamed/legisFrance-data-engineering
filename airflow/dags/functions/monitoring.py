import time
from airflow.configuration import conf
from statsd import StatsClient

STATSD_HOST = conf.get("metrics", "statsd_host")
STATSD_PORT = conf.get("metrics", "statsd_port")
STATSD_PREFIX = conf.get("metrics", "statsd_prefix")

stats = StatsClient(host=STATSD_HOST, port=STATSD_PORT, prefix=STATSD_PREFIX)

dag_id = 'legifrance-data-eng'

dag_duration_metric_name =  f'dag.{dag_id}.dag_duration'


def on_failure_callback(context):
    task_instance = context.get('task_instance')
    dag_id = task_instance.dag_id
    task_id = task_instance.task_id
    task_failed_metric_name = f'dag.{dag_id}.{task_id}.failed'
    stats.gauge(task_failed_metric_name, 1)
    
    # stats.timing(dag_duration_metric_name, -1 * 1000)

def on_success_callback(context):
    task_instance = context.get('task_instance')
    dag_id = task_instance.dag_id
    task_id = task_instance.task_id
    task_failed_metric_name = f'dag.{dag_id}.{task_id}.failed'
    stats.gauge(task_failed_metric_name, 0)



def start_time(start_time, **kwargs):
    kwargs['ti'].xcom_push(key="start_time", value=start_time)

def end_time(**kwargs):
   start_time = kwargs['ti'].xcom_pull(key="start_time")
   end_time = time.time()
   duration = int((end_time - start_time ))
   stats.timing(dag_duration_metric_name, duration * 1000)
