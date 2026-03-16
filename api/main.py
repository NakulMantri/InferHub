from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.routes import api_router
from core.logger import logger
from database.db import init_db
from cache.redis_client import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up LLM Inference Gateway")
    await init_db()
    await redis_client.connect()
    yield
    # Shutdown
    logger.info("Shutting down")
    await redis_client.disconnect()

app = FastAPI(
    title="LLM Inference Gateway",
    description="Unified API gateway for multiple LLMs with caching and metrics",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router)
