from fastapi import FastAPI
from src.monitoring.otel_setup import setup_otel_logging
from src.api.core.lifespan import lifespan
from src.api.routes.health import router as health_router
from src.api.routes.tracks import router as tracks_router
from src.api.routes.dbt import router as dbt_router
from src.api.routes.load_db import router as load_db_router

setup_otel_logging("otel-collector", 4318)

app = FastAPI(title="Goats API", description="API to run ELT jobs", lifespan=lifespan)

app.include_router(health_router)
app.include_router(tracks_router)
app.include_router(load_db_router)
app.include_router(dbt_router)
