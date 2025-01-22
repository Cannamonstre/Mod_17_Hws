from fastapi import FastAPI
from app.backend.db import engine, Base
from app.models.task import router as task_router
from app.models.user import router as user_router

app = FastAPI()


@app.get("/")
async def main_page() -> dict:
    return {"message": "Welcome to Taskmanager"}


app.include_router(task_router)
app.include_router(user_router)

Base.metadata.create_all(bind=engine)
