from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import settings
from core.logger import logger
from database.models import Base

engine = create_async_engine(settings.database_url, echo=False)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized.")

async def get_db_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def log_inference(
    model_used: str,
    prompt_length: int,
    response_length: int,
    latency_ms: float
):
    from database.models import InferenceLog
    async with async_session_maker() as session:
        log_entry = InferenceLog(
            model_used=model_used,
            prompt_length=prompt_length,
            response_length=response_length,
            latency_ms=latency_ms
        )
        session.add(log_entry)
        await session.commit()
    logger.info(f"Logged inference to db: {model_used}, latency {latency_ms:.2f}ms")
