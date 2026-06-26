from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, Session

from ..auth import CurrentUser
from ..db.database import SessionDep
from ..models.models import Habits, Categories
from ..schemas.schemas import CreateHabitRequest, UpdateHabitRequest

router = APIRouter(prefix="/habits", tags=["Habits"])


def _get_owned_habit(habit_id: int, user_id: str, session: Session) -> Habits:
    habit = session.exec(
        select(Habits).where(Habits.id == habit_id, Habits.user_id == user_id)
    ).one_or_none()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


def _assert_category_owned(category_id: int, user_id: str, session: Session) -> None:
    category = session.exec(
        select(Categories).where(Categories.id == category_id, Categories.user_id == user_id)
    ).one_or_none()
    if not category:
        raise HTTPException(status_code=400, detail=f"Category {category_id} not found")


@router.get("", summary="List habits")
def list_habits(user_id: CurrentUser, session: SessionDep) -> List[Habits]:
    """Return every habit owned by the current user."""
    return session.exec(select(Habits).where(Habits.user_id == user_id)).all()


@router.get("/{habit_id}", summary="Get a habit")
def get_habit(habit_id: int, user_id: CurrentUser, session: SessionDep) -> Habits:
    """Return a single habit by id. 404 if it doesn't exist or isn't yours."""
    return _get_owned_habit(habit_id, user_id, session)


@router.post("", summary="Create a habit", status_code=status.HTTP_201_CREATED)
def create_habit(request: CreateHabitRequest, user_id: CurrentUser, session: SessionDep) -> Habits:
    """Create a new habit for the current user. `category_id` is optional;
    if provided, it must reference a category the current user owns."""
    if request.category_id is not None:
        _assert_category_owned(request.category_id, user_id, session)

    new_habit = Habits(**request.model_dump(), user_id=user_id)
    session.add(new_habit)
    session.commit()
    session.refresh(new_habit)
    return new_habit


@router.patch("/{habit_id}", summary="Update a habit")
def update_habit(habit_id: int, request: UpdateHabitRequest, user_id: CurrentUser, session: SessionDep) -> Habits:
    """Partial update. Only fields present in the body are changed.
    If `category_id` is provided, it must reference a category the current user owns."""
    habit = _get_owned_habit(habit_id, user_id, session)

    updates = request.model_dump(exclude_unset=True)
    if "category_id" in updates and updates["category_id"] is not None:
        _assert_category_owned(updates["category_id"], user_id, session)

    for key, value in updates.items():
        setattr(habit, key, value)
    habit.updated_at = datetime.now()

    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@router.delete("/{habit_id}", summary="Delete a habit", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int, user_id: CurrentUser, session: SessionDep) -> None:
    """Delete a habit. Also deletes its completion logs (via the habit_logs.habit_id FK)."""
    habit = _get_owned_habit(habit_id, user_id, session)
    session.delete(habit)
    session.commit()
