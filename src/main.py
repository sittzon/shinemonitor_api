from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.endpoints import router as api_router
from services.cache import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Shinemonitor API",
    description="API to access data from shinemonitor.com",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan)

app.include_router(api_router)