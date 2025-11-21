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
    endpoint=f"/health",
    dag=dag,
)

extract_and_load = HttpOperator(
    task_id="extract_and_load",
    method="POST",
    http_conn_id="goats_api_connection",
    endpoint=f"/recently_played_tracks",
    dag=dag,
)

# konrad (load from minio to posgres)
# ...

dbt_build = HttpOperator(
    task_id="dbt_build",
    method="POST",
    http_conn_id="goats_api_connection",
    endpoint=f"/dbt_build",
    dag=dag,
)

check_goats_api >> extract_and_load >> dbt_build
