from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime

dag = DAG(
    dag_id="hello_world",
    start_date=datetime(2025, 11, 14),
    schedule=None,
    catchup=False,
)


def hello_world():
    print("Hello World from Airflow!")


task_hello = PythonOperator(
    task_id="print_hello",
    python_callable=hello_world,
    dag=dag,
)

task_hello
