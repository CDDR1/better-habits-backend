from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, func, desc, distinct

from ..db.database import SessionDep
from ..models.models import Habits, HabitLogs, Categories, HabitsCategoriesLink
from ..schemas.schemas import UpsertHabitRequest, UpdateHabitCategoriesRequest, DeleteHabitResponse, \
    ReorderHabitsRequest, ReorderHabitsResponse

router = APIRouter()

# TODO: Might want to delete this endpoint after development, as there is no need to get all the habits
@router.get("/habits")
def get_habits(session: SessionDep):
    habits = session.exec(select(Habits)).all()
    return habits

@router.get("/users/{user_id}/habits")
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
    # TODO: Add input validation to avoid adding categories that already exist
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
    new_habit = Habits(**habit.model_dump())
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

    updated_habit_dict = updated_habit.model_dump(exclude_unset=True)
    for key, value in updated_habit_dict.items():
        setattr(habit, key, value)

    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit

def balance_display_order_fields(deleted_display_order: int, session: SessionDep):
    """
    Updates the display_order fields to remove gaps and ensure they are sequential, typically after habit deletion.
    :param deleted_display_order: integer
    :param session: SessionDep
    """
    statement = select(Habits).where(Habits.display_order > deleted_display_order)
    habits_to_update = session.exec(statement).all()

    for habit in habits_to_update:
        habit.display_order = habit.display_order - 1

    if habits_to_update:
        session.add_all(habits_to_update)
        session.commit()

@router.delete("/habits/{habit_id}")
def delete_habit(habit_id: int, session: SessionDep) -> DeleteHabitResponse:
    statement = select(Habits).where(Habits.id == habit_id)
    habit = session.exec(statement).one()
    session.delete(habit)
    session.commit()

    # confirm habit was deleted
    deleted_habit = session.exec(statement).first()
    if deleted_habit is not None:
        # TODO: Raise an exception
        pass

    balance_display_order_fields(habit.display_order, session)
    response = DeleteHabitResponse(is_success=True)
    return response

@router.patch("/habits-reorder")
def reorder_habits(request_body: ReorderHabitsRequest, session: SessionDep) -> ReorderHabitsResponse:
    habits_to_reorder = request_body.habits_to_reorder
    habits_to_reorder_ids = {habit.id for habit in habits_to_reorder}
    if len(habits_to_reorder_ids) != len(habits_to_reorder):
        raise HTTPException(status_code=400, detail=f"Duplicate habit IDs found in request")

    id_to_display_order_dict = {habit.id: habit.display_order for habit in habits_to_reorder}
    statement = select(Habits).where(Habits.id.in_(id_to_display_order_dict.keys()))
    habits = session.exec(statement).all()

    found_ids = {habit.id for habit in habits}
    missing_ids = habits_to_reorder_ids - found_ids
    if missing_ids:
        raise HTTPException(status_code=400, detail=f"Not all habit IDs in the request were found - missing IDs: {sorted(missing_ids)}")

    for habit in habits:
        habit.display_order = id_to_display_order_dict[habit.id]

    session.add_all(habits)
    session.commit()
    response = ReorderHabitsResponse(is_success=True)
    return response

@router.get("/habits-by-categories")
def get_habits_by_categories(category_ids: Annotated[List[int], Query()], session: SessionDep) -> List[Habits]:
    """
    Returns habits filtered by one or multiple categories
    :return:
    """

    # TODO: Add validation for category ids

    statement = (
        select(HabitsCategoriesLink.habit_fk)
        .where(HabitsCategoriesLink.category_fk.in_(category_ids))
        .group_by(HabitsCategoriesLink.habit_fk)
        .having(func.count(distinct(HabitsCategoriesLink.category_fk)) == len(category_ids))
    )

    habits_ids = session.exec(statement).all()
    habits = session.exec(select(Habits).where(Habits.id.in_(habits_ids)))
    return habits