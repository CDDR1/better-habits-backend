from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db.database import engine
from app.models import models  # noqa: F401 — import registers tables on SQLModel.metadata
from app.routers import habits, categories, habit_logs


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Better Habits API",
    description=(
        "Backend for the Better Habits app. Lets users create habits, organize them "
        "into categories, and mark them as completed on a given day."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(habits.router)
app.include_router(categories.router)
app.include_router(habit_logs.router)


@app.get("/", tags=["Health"], summary="Health check")
def read_root():
    """Returns a simple hello payload so you can verify the API is up."""
    return {"Hello": "World!"}
