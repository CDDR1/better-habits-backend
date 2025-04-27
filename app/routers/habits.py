from fastapi import APIRouter
from ..db.database import SessionDep
from sqlmodel import select, func, desc
from ..models.models import Habits, HabitLogs, Categories
from ..schemas.schemas import UpsertHabitRequest, UpdateHabitCategoriesRequest

router = APIRouter()

# TODO: Might want to delete this endpoint after development, as there is no need to get all the habits
@router.get("/habits")
def get_habits(session: SessionDep):
    habits = session.exec(select(Habits)).all()
    return habits

@router.get("/user/{user_id}/habits")
def get_habits_for_user(user_id: int, session: SessionDep):
    statement = select(Habits).where(Habits.user_fk == user_id).order_by(desc(Habits.display_order))
    habits = session.exec(statement).all()
    return habits

@router.get("/habits/{habit_id}/categories")
def get_categories_for_habit(habit_id: int, session: SessionDep):
    statement = select(Habits).where(Habits.id == habit_id)
    habit = session.exec(statement).one_or_none()
    return habit.categories

@router.post("/habits/{habit_id}/categories")
def add_categories_for_habit(habit_id: int, request_body: UpdateHabitCategoriesRequest, session: SessionDep):
    habit = session.exec(select(Habits).where(Habits.id == habit_id)).one()

    for category_id in request_body.category_ids:
        category = session.exec(select(Categories).where(Categories.id == category_id)).one()
        habit.categories.append(category)

    session.add(habit)
    session.commit()
    return habit.categories

@router.delete("/habits/{habit_id}/categories")
def delete_category_from_habit(habit_id: int, request_body: UpdateHabitCategoriesRequest, session: SessionDep):
    habit = session.exec(select(Habits).where(Habits.id == habit_id)).one()

    for category_id in request_body.category_ids:
        category = session.exec(select(Categories).where(Categories.id == category_id)).one()
        habit.categories.remove(category)

    session.add(habit)
    session.commit()
    return habit.categories

@router.get("/habits/{habit_id}/logs")
def get_habit_logs_for_habit(habit_id: int, session: SessionDep):
    statement = select(HabitLogs).where(HabitLogs.habit_fk == habit_id)
    habit_logs = session.exec(statement).all()
    return habit_logs

@router.post("/habits")
def create_habit(habit: UpsertHabitRequest, session: SessionDep):
    new_habit = Habits(**habit.dict())
    get_greatest_display_order_statement = select(func.max(Habits.display_order))
    greatest_display_order = session.exec(get_greatest_display_order_statement).one()
    new_habit.display_order = (greatest_display_order or 0) + 1
    session.add(new_habit)
    session.commit()
    session.refresh(new_habit)
    return new_habit

@router.patch("/habits/{habit_id}")
def update_habit(habit_id: int, updated_habit: UpsertHabitRequest, session: SessionDep):
    get_habit_statement = select(Habits).where(Habits.id == habit_id)
    habit = session.exec(get_habit_statement).one()

    updated_habit_dict = updated_habit.dict(exclude_unset=True)
    for key, value in updated_habit_dict.items():
        setattr(habit, key, value)

    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit

@router.delete("/habits/{habit_id}")
def delete_habit(habit_id: int, session: SessionDep):
    statement = select(Habits).where(Habits.id == habit_id)
    habit = session.exec(statement).one()
    session.delete(habit)
    session.commit()

    # confirm habit was deleted
    habit = session.exec(statement).first()
    if habit != None:
        # TODO: Raise an exception
        pass
