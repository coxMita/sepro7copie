import logging

from fastapi import FastAPI

from src.routers.desk_integration import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.info("Starting Desk Integration Service...")
app = FastAPI()
app.include_router(router)


@app.get("/")
def get_root() -> dict[str, str]:
    """Root endpoint providing basic service information."""
    return {"service": "Desk Integration Service"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
