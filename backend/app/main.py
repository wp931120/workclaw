"""WorkClaw FastAPI application."""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import get_settings
from app.capabilities.bootstrap import bootstrap_capabilities


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    print(f"Starting {settings.app_name} v{settings.app_version}")

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