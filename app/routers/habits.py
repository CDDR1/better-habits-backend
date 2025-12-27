from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, func, desc, distinct
from datetime import date, datetime

from ..db.database import SessionDep
from ..models.models import Habits, HabitLogs, Categories, HabitsCategoriesLink
from ..schemas.schemas import UpsertHabitRequest, UpdateHabitCategoriesRequest, DeleteHabitResponse, \
    ReorderHabitsRequest, ReorderHabitsResponse

router = APIRouter()

# TODO: Add docstring comments
# TODO: Move the logic and helper functions of these endpoints to the services directory

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

def is_today_in_list_of_specific_weekdays(repeat_config: str):
    if not repeat_config:
        return False

    weekdays = repeat_config.split(",")
    today = date.today().weekday()
    weekday_strings = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
    return weekday_strings[today].lower() in [weekday.lower() for weekday in weekdays]

def is_today_in_list_of_specific_month_days(repeat_config: str):
    if not repeat_config:
        return False

    month_days = repeat_config.split(",")
    today = datetime.today().day
    return today in [int(day) for day in month_days]

def is_n_times_per_week_goal_met(repeat_config: str, habit_id: int, session: SessionDep):
    if not repeat_config:
        return False

    n = int(repeat_config)
    statement = (select(HabitLogs)
                 .where(HabitLogs.habit_fk == habit_id)
                 .order_by(desc(HabitLogs.created_at))
                 .limit(n))
    last_n_habit_logs = session.exec(statement).all()
    if not last_n_habit_logs:
        return False

    oldest_log_date = last_n_habit_logs[-1].created_at
    oldest_log_year_and_week = oldest_log_date.isocalendar()[:2]
    today_year_and_week = date.today().isocalendar()[:2]
    return oldest_log_year_and_week == today_year_and_week

def is_n_times_per_month_goal_met(repeat_config: str, habit_id: int, session: SessionDep):
    if not repeat_config:
        return False

    n = int(repeat_config)
    statement = (select(HabitLogs)
                 .where(HabitLogs.habit_fk == habit_id)
                 .order_by(desc(HabitLogs.created_at))
                 .limit(n))
    last_n_habit_logs = session.exec(statement).all()
    if not last_n_habit_logs or len(last_n_habit_logs) < n:
        return False

    oldest_log_date = last_n_habit_logs[-1].created_at
    today = date.today()
    return oldest_log_date.month == today.month

@router.get("/users/{user_id}/habits-for-today")
def get_habits_to_complete_today(user_id: int, session: SessionDep):
    statement = select(Habits).where(Habits.user_fk == user_id).order_by(desc(Habits.display_order))
    habits = session.exec(statement).all()

    habits_to_complete_ids = []
    for habit in habits:
        # TODO: Add enum for repeat types
        repeat_type = habit.repeat_type
        match repeat_type:
            case "DAILY":
                habits_to_complete_ids.append(habit.id)
            case "SPECIFIC_WEEKDAYS":
                if is_today_in_list_of_specific_weekdays(habit.repeat_config):
                    habits_to_complete_ids.append(habit.id)
            case "SPECIFIC_MONTH_DAYS":
                if is_today_in_list_of_specific_month_days(habit.repeat_config):
                    habits_to_complete_ids.append(habit.id)
            case "N_TIMES_PER_WEEK":
                if not is_n_times_per_week_goal_met(habit.repeat_config, habit.id, session):
                    habits_to_complete_ids.append(habit.id)
            case "N_TIMES_PER_MONTH":
                if not is_n_times_per_month_goal_met(habit.repeat_config, habit.id, session):
                    habits_to_complete_ids.append(habit.id)
            case "EVERY_N_DAYS":
                pass

    return habits_to_complete_ids

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
    :param deleted_display_order: display order of the deleted habit
    :param session: current DB session
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
    :param category_ids: Query parameter that contains a list of category iDs to filter habits by
    :param session: current DB session
    :return: list of Habits
    """
    validate_category_ids_statement = select(Categories.id).where(Categories.id.in_(category_ids))
    found_category_ids = session.exec(validate_category_ids_statement).all()
    if len(found_category_ids) != len(category_ids):
        categories_not_found = set(category_ids) - set(found_category_ids)
        raise HTTPException(status_code=400, detail=f"Not all category IDs in the request were found - missing IDs: {sorted(categories_not_found)}")

    habits_by_categories_statement = (
        select(HabitsCategoriesLink.habit_fk)
        .where(HabitsCategoriesLink.category_fk.in_(category_ids))
        .group_by(HabitsCategoriesLink.habit_fk)
        .having(func.count(distinct(HabitsCategoriesLink.category_fk)) == len(category_ids))
    )
    habits_ids = session.exec(habits_by_categories_statement).all()

    get_habits_statement = select(Habits).where(Habits.id.in_(habits_ids))
    habits = session.exec(get_habits_statement)
    return habits