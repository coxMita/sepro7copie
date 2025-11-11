import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.dependencies import get_db_session
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

        # Load schedules from database
        logger.info("Loading schedules from database...")
        db_session = next(get_db_session())
        try:
            scheduler_service.load_schedules_from_db(db_session)
        finally:
            db_session.close()

        # Check if any schedules were loaded
        jobs = scheduler_service.get_all_jobs()
        logger.info(f"Total jobs after database load: {len(jobs)}")

        # If no schedules exist, create defaults
        if len(jobs) == 0:
            logger.info("No schedules found in database. Creating defaults...")
            db_session = next(get_db_session())
            try:
                scheduler_service.setup_default_schedules(db_session)
            finally:
                db_session.close()

            # Verify defaults were created
            jobs = scheduler_service.get_all_jobs()
            logger.info(f"Total jobs after creating defaults: {len(jobs)}")

        # Log all schedules
        if jobs:
            logger.info("Active schedules:")
            for job in jobs:
                jid = job.get("id") or job.get("job_id")
                jname = job.get("name") or job.get("job_name") or "<unnamed>"
                next_run = job.get("next_run") or "not scheduled"
                logger.info(f"  ✓ {jid}: {jname} (next: {next_run})")
        else:
            logger.warning("  ⚠ No jobs were created!")

    except Exception as e:
        logger.exception(f"ERROR during startup: {e}")

    # Yield to serve requests
    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info("APPLICATION SHUTDOWN")
    logger.info("=" * 60)
    try:
        if hasattr(scheduler_service, "shutdown"):
            scheduler_service.shutdown()
        rabbitmq_client.disconnect()
    except Exception as e:  # noqa: BLE001
        logger.exception(f"Error during shutdown: {e}")


# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI(
    title="Desk Scheduler Service",
    version="1.1.0",
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
    return {
        "service": "Desk Scheduler Service",
        "status": "running",
        "version": "1.1.0",
    }


@app.get("/debug/setup")
def debug_setup() -> dict[str, object]:
    """Manually trigger default schedule setup."""
    try:
        db_session = next(get_db_session())
        try:
            scheduler_service.setup_default_schedules(db_session)
        finally:
            db_session.close()

        jobs = scheduler_service.get_all_jobs()
        return {
            "status": "success",
            "message": f"Setup called, {len(jobs)} jobs exist",
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
