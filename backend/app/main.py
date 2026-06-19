"""WorkClaw FastAPI application."""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import get_settings
from app.capabilities.bootstrap import bootstrap_capabilities
from app.models.database import init_db, async_session_factory
from app.models.user import User, UserRole
from app.models.session import Session, SessionStatus
from sqlmodel import select


async def ensure_dev_user() -> None:
    """Ensure a dev user exists for local development."""
    if async_session_factory is None:
        return
    async with async_session_factory() as session:
        # Check if dev user exists
        stmt = select(User).where(User.email == "dev@workclaw.local")
        result = await session.exec(stmt)
        dev_user = result.first()
        if not dev_user:
            # Create dev user
            dev_user = User(
                email="dev@workclaw.local",
                name="Dev User",
                role=UserRole.admin,
            )
            session.add(dev_user)
            await session.commit()
            # Also create a default session
            stmt = select(Session).where(Session.user_id == dev_user.id)
            result = await session.exec(stmt)
            if not result.first():
                default_session = Session(
                    user_id=dev_user.id,
                    title="Welcome Session",
                    model_profile="claude-glm-5.1",
                    status=SessionStatus.active,
                )
                session.add(default_session)
                await session.commit()
            print("[WorkClaw] Created dev user: dev@workclaw.local")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    print(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize database
    await init_db()
    await ensure_dev_user()

    # Bootstrap capabilities
    bootstrap_capabilities()

    yield

    # Shutdown
    print("Shutting down WorkClaw...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    from app.api.v1 import health, auth, chat, capabilities, tasks

    api_router = APIRouter(prefix="/api/v1")
    api_router.include_router(health.router, tags=["health"])
    api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
    api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
    api_router.include_router(capabilities.router, tags=["capabilities"])
    api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

    # Alias routes for cleaner API design:
    # /api/v1/sessions -> /api/v1/chat/sessions
    # /api/v1/tasks -> /api/v1/tasks/tasks (already the case)
    api_router.include_router(chat.router, prefix="", tags=["chat-alias"])
    api_router.include_router(tasks.router, prefix="", tags=["tasks-alias"])

    app.include_router(api_router)

    return app


app = create_app()