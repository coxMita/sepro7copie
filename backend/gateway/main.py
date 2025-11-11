from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.booking_proxy import router
from src.routers.occupancy_proxy import router as occupancy_router
from src.routers.scheduler_proxy import router as scheduler_router

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(occupancy_router)
app.include_router(scheduler_router)


@app.get("/")
def get_root() -> dict:
    """Root endpoint returning a welcome message."""
    return {"message": "Welcome to the API Gateway"}


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
