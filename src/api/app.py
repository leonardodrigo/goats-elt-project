from fastapi import FastAPI
from src.api.core.lifespan import lifespan
from src.api.routes.health import router as health_router
from src.api.routes.tracks import router as tracks_router
from src.api.routes.load import router as postgres_router
from src.api.routes.dbt import router as dbt_router

app = FastAPI(title="Goats API", description="API to run ELT jobs", lifespan=lifespan)

app.include_router(health_router)
app.include_router(tracks_router)
app.include_router(postgres_router)
app.include_router(dbt_router)
