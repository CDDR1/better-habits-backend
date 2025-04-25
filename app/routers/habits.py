from fastapi import APIRouter
from ..db.database import SessionDep
from sqlmodel import select, func
from ..models.models import Habits, HabitLogs
from ..schemas.schemas import HabitCreate

router = APIRouter()

# TODO: Might want to delete this endpoint after development, as there is no need to get all the habits
@router.get("/habits")
def get_habits(session: SessionDep):
    habits = session.exec(select(Habits)).all()
    return habits

@router.get("/user/{user_id}/habits")
def get_habits_for_user(user_id: int, session: SessionDep):
    statement = select(Habits).where(Habits.user_fk == user_id)
    habits = session.exec(statement).all()
    return habits

@router.get("/habits/{habit_id}/categories")
def get_categories_for_habit(habit_id: int, session: SessionDep):
    statement = select(Habits).where(Habits.id == habit_id)
    habit = session.exec(statement).one_or_none()
    return habit.categories

@router.get("/habits/{habit_id}/logs")
def get_habit_logs_for_habit(habit_id: int, session: SessionDep):
    statement = select(HabitLogs).where(HabitLogs.habit_fk == habit_id)
    habit_logs = session.exec(statement).all()
    return habit_logs

@router.post("/habits")
def create_habit(habit: HabitCreate, session: SessionDep):
    new_habit = Habits(**habit.dict())
    get_greatest_display_order_statement = select(func.max(Habits.display_order))
    display_order = session.exec(get_greatest_display_order_statement).one()
    new_habit.display_order = (display_order or 0) + 1
    session.add(new_habit)
    session.commit()
    session.refresh(new_habit)
    return new_habit

@router.delete("/habits/{habit_id}")
def delete_habit(habit_id: int, session: SessionDep):
    statement = select(Habits).where(Habits.id == habit_id)
    habit = session.exec(statement).one_or_none()
    session.delete(habit)
