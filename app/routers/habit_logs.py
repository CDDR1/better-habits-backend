from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..auth import CurrentUser
from ..db.database import SessionDep
from ..models.models import HabitLogs, Habits

router = APIRouter(prefix="/habits/{habit_id}/logs", tags=["Habit Logs"])


def _assert_habit_owned(habit_id: int, user_id: str, session) -> None:
    habit = session.exec(
        select(Habits).where(Habits.id == habit_id, Habits.user_id == user_id)
    ).one_or_none()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")


@router.get("", summary="List completions for a habit")
def list_completions(habit_id: int, user_id: CurrentUser, session: SessionDep) -> List[HabitLogs]:
    """Return every completion log for the given habit, oldest first."""
    _assert_habit_owned(habit_id, user_id, session)
    return session.exec(
        select(HabitLogs).where(HabitLogs.habit_id == habit_id).order_by(HabitLogs.completed_on)
    ).all()


@router.post("", summary="Mark habit completed")
def mark_completed(habit_id: int, user_id: CurrentUser, session: SessionDep) -> HabitLogs:
    """Mark a habit as completed for today. The date comes from the server clock
    (never from the client) to avoid issues where users have an incorrect system date.
    Idempotent: if a log already exists for that habit + today, the existing row is returned."""
    _assert_habit_owned(habit_id, user_id, session)
    completed_on = date.today()

    existing = session.exec(
        select(HabitLogs).where(
            HabitLogs.habit_id == habit_id, HabitLogs.completed_on == completed_on
        )
    ).one_or_none()
    if existing:
        return existing

    log = HabitLogs(habit_id=habit_id, completed_on=completed_on)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


@router.delete("/{completed_on}", summary="Unmark habit completion", status_code=status.HTTP_204_NO_CONTENT)
def unmark_completed(habit_id: int, completed_on: date, user_id: CurrentUser, session: SessionDep) -> None:
    """Remove the completion log for the given habit and date. 404 if no such log exists."""
    _assert_habit_owned(habit_id, user_id, session)
    log = session.exec(
        select(HabitLogs).where(
            HabitLogs.habit_id == habit_id, HabitLogs.completed_on == completed_on
        )
    ).one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="No log found for that date")

    session.delete(log)
    session.commit()
