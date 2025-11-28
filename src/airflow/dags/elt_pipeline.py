from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from datetime import datetime 


dag = DAG(
    dag_id="goats_elt_pipeline",
    start_date=datetime(2025, 11, 14),
    schedule=None,
    catchup=False,
)

check_goats_api = HttpOperator(
    task_id="check_goats_api",
    method="GET",
    http_conn_id="goats_api_connection",
    endpoint="/health",
    dag=dag,
)

extract_and_load = HttpOperator(
    task_id="extract_and_load",
    method="POST",
    http_conn_id="goats_api_connection",
    endpoint="/recently_played_tracks",
    dag=dag,
)
dbt_build = HttpOperator(
    task_id="dbt_build",
    method="POST",
    http_conn_id="goats_api_connection",
    endpoint="/dbt_build",
    dag=dag,
)

load_to_db = HttpOperator(
    task_id="load_to_db",
    method="POST",
    http_conn_id="goats_api_connection",
    endpoint=f"/load_db",
    dag=dag,
)

check_goats_api >> extract_and_load >> load_to_db >> dbt_build
