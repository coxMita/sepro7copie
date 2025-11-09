from fastapi import FastAPI

from src.routers.bookings import router

app = FastAPI()
app.include_router(router)


@app.get("/")
def get_root():
    return {"Hello": "World"}
