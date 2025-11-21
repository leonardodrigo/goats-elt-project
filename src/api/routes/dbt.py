from fastapi import APIRouter
from dbt.cli.main import dbtRunner

router = APIRouter()


@router.post(
    "/dbt_build",
    description="Runs a DBT job to transform data in Postgres",
)
def dbt_build():
    dbt = dbtRunner()
    res = dbt.invoke(["build"])
    return {"success": True, "results": res.result}