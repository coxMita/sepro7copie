import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import scheduler as scheduler_router
from src.services.rabbitmq_client import rabbitmq_client
from src.services.scheduler_service import scheduler_service

# ----------------------------
# Logging
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("desk-scheduler-service")


# ----------------------------
# Lifespan (startup / shutdown)
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup and shutdown lifecycle."""
    # Startup
    logger.info("=" * 60)
    logger.info("APPLICATION STARTUP")
    logger.info("=" * 60)

    try:
        logger.info("Connecting to RabbitMQ broker...")
        rabbitmq_client.connect()

        if (
            hasattr(scheduler_service, "is_running")
            and not scheduler_service.is_running()
            and hasattr(scheduler_service, "start")
        ):
            logger.info("Starting scheduler service...")
            scheduler_service.start()

        logger.info("Calling setup_default_schedules()...")
        scheduler_service.setup_default_schedules()

        jobs = scheduler_service.get_all_jobs()
        logger.info("Schedules initialized. Total jobs: %d", len(jobs))
        if jobs:
            for job in jobs:
                # support both 'id' and 'job_id' keys, depending on your service
                jid = job.get("id") or job.get("job_id")
                jname = job.get("name") or job.get("job_name") or "<unnamed>"
                logger.info("  ✓ %s: %s", jid, jname)
        else:
            logger.warning("  ⚠ No jobs were created!")
    except Exception as e:
        logger.exception("ERROR during startup: %s", e)

    # Yield to serve requests
    yield

    # Shutdown
    logger.info("APPLICATION SHUTDOWN")
    try:
        if hasattr(scheduler_service, "shutdown"):
            scheduler_service.shutdown()
            rabbitmq_client.disconnect()
    except Exception as e:  # noqa: BLE001
        logger.exception("Error during shutdown: %s", e)


# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI(
    title="Desk Scheduler Service",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS (tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # e.g. ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(scheduler_router.router)


# ----------------------------
# Debug / Utility endpoints
# ----------------------------
@app.get("/")
def get_root() -> dict[str, str]:
    """Health endpoint for the Scheduler Service."""
    return {"service": "Desk Scheduler Service", "status": "running"}


@app.get("/debug/setup")
def debug_setup() -> dict[str, object]:
    """Manually trigger default schedule setup."""
    try:
        scheduler_service.setup_default_schedules()
        jobs = scheduler_service.get_all_jobs()
        return {
            "status": "success",
            "message": "Setup called, %d jobs exist" % len(jobs),
            "jobs": jobs,
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": str(e)}


@app.get("/debug/jobs")
def debug_jobs() -> dict[str, object]:
    """Inspect current jobs."""
    jobs = scheduler_service.get_all_jobs()
    running = getattr(scheduler_service, "is_running", lambda: None)()
    return {
        "scheduler_running": running,
        "jobs_count": len(jobs),
        "jobs": jobs,
    }
