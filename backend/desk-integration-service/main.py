from fastapi import FastAPI

from src.routers.desk_integration import router

app = FastAPI()
app.include_router(router)


@app.get("/")
def get_root():
    return {"Hello": "World"}
