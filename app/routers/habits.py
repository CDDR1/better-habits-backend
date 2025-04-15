from fastapi import APIRouter
from ..db.database import SessionDep
from ..models.habits_model import Habits
from sqlmodel import select

router = APIRouter()


@router.get("/habits", tags=["habits"])
async def read_users(session: SessionDep):
    habits = session.exec(select(Habits)).all()
    return habits