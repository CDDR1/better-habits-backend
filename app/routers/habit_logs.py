from datetime import date

from fastapi import APIRouter, Response, status
from ..db.database import SessionDep
from ..models.models import Habits, HabitLogs
from sqlmodel import select, func
from ..schemas.schemas import UpsertHabitLogRequest

router = APIRouter()

@router.put("/habits/{habit_id}/logs/{date}")
def upsert_habit_log(request_body: UpsertHabitLogRequest, habit_id: int, date: date, response: Response, session: SessionDep):
    statement = select(HabitLogs).where(HabitLogs.habit_fk == habit_id).where(func.date(HabitLogs.created_at) == date)
    habit_log = session.exec(statement).one_or_none()
    request_body_dict = request_body.model_dump(exclude_unset=True)

    if habit_log:
        habit_log_dict = habit_log.model_dump()
        del habit_log_dict["created_at"]
        del habit_log_dict["updated_at"]

        if habit_log_dict["goal_value"] is None:
            del habit_log_dict["goal_value"]
        if habit_log_dict["goal_unit"] is None:
            del habit_log_dict["goal_unit"]

        if request_body_dict == habit_log_dict:
            response.status_code = status.HTTP_200_OK
            return habit_log

        habit_log.progress_value = request_body.progress_value
        habit_log.note = request_body.note
        habit_log.goal_value = request_body.goal_value
        habit_log.goal_value = request_body.goal_unit
        habit_log.completion_percentage = request_body.completion_percentage
        session.add(habit_log)
        session.commit()
        session.refresh(habit_log)
        response.status_code = status.HTTP_200_OK
        return habit_log
    else:
        new_habit_log = HabitLogs(**request_body_dict, habit_fk=habit_id)
        session.add(new_habit_log)
        session.commit()
        session.refresh(new_habit_log)
        response.status_code = status.HTTP_201_CREATED
        return new_habit_log
