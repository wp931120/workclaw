"""Database engine and session management."""

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.config.settings import get_settings


engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db() -> None:
    """Initialize database engine and create tables."""
    global engine, async_session_factory

    settings = get_settings()
    engine = AsyncEngine(
        __import__("sqlalchemy").create_async_engine(settings.database_url, echo=settings.debug)
    )
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency for getting async database session."""
    if async_session_factory is None:
        await init_db()
    assert async_session_factory is not None
    async with async_session_factory() as session:
        yield session
