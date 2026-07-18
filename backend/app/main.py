from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.database.session import engine, Base
from app.core.settings import settings
from app.core.logging import logger
from app.core.exceptions import register_exception_handlers

from app.services.background_indexer import initialize_watcher_triggers, stop_watcher_triggers

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Lifespan handler mapping database generation on startup and cleanup on shutdown."""
    logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("SQLite database tables verification/creation completed.")
    except Exception as e:
        logger.error(f"Critical: Failed to generate SQLite tables: {e}")
        
    # Start background file monitor watcher
    initialize_watcher_triggers()
    
    yield
    
    # Stop background watcher loops
    stop_watcher_triggers()
    logger.info("Shutting down backend, closing connections...")

def create_app() -> FastAPI:
    """Application factory building and configuring the PEIS FastAPI instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register custom exception handlers (ValidationException, DBError handlers)
    register_exception_handlers(app)

    # Mount endpoints
    app.include_router(api_router)

    # Health API routes (Phase 1 SPEC)
    @app.get("/health", tags=["System Status"])
    def get_health():
        """Basic health check endpoint."""
        return {"status": "healthy"}

    @app.get("/version", tags=["System Status"])
    def get_version():
        """Returns the current application version."""
        return {"version": settings.VERSION}

    @app.get("/status", tags=["System Status"])
    def get_status():
        """Returns extended status details of the backend services."""
        return {
            "status": "online",
            "app_name": settings.PROJECT_NAME,
            "llm_provider": settings.ACTIVE_LLM_PROVIDER,
            "database": "connected"
        }

    return app

app = create_app()
