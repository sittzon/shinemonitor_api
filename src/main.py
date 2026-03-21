from fastapi import FastAPI
from api.endpoints import router as api_router

app = FastAPI(
    title="Shinemonitor API",
    description="API to access data from shinemonitor.com",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json")

app.include_router(api_router)