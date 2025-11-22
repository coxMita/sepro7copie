import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.messaging.rabbitmq_publisher import rabbitmq_publisher
from src.routers.desk_integration import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events for RabbitMQ publishing.

    This context manager handles:
    - Startup: Initialize RabbitMQ connection for publishing events
    - Shutdown: Gracefully close RabbitMQ connection

    Args:
        app (FastAPI): The FastAPI application instance.

    """
    # Startup: Initialize RabbitMQ publisher
    logger.info("=" * 60)
    logger.info("Starting Desk Integration Service...")
    logger.info("=" * 60)

    try:
        logger.info("Connecting to RabbitMQ for event publishing...")
        rabbitmq_publisher.connect()
        logger.info("✓ RabbitMQ publisher initialized successfully")
    except Exception as e:
        logger.warning("⚠ RabbitMQ connection failed: %s", e)
        logger.info("Service will continue without event publishing")

    yield

    # Shutdown: Clean up messaging
    logger.info("=" * 60)
    logger.info("Shutting down Desk Integration Service...")
    logger.info("=" * 60)
    try:
        rabbitmq_publisher.disconnect()
        logger.info("✓ RabbitMQ connection closed")
    except Exception as e:
        logger.error("✗ Error during shutdown: %s", e)


app = FastAPI(
    title="Desk Integration Service",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def get_root() -> dict[str, str]:
    """Root endpoint providing basic service information."""
    return {
        "service": "Desk Integration Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}