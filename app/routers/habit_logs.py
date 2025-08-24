from collections import defaultdict
from datetime import date, timedelta, datetime
from typing import Dict, Tuple, List

from fastapi import APIRouter, Response, status
from sqlmodel import select, func
from ..db.database import SessionDep
from ..models.models import HabitLogs
from ..schemas.schemas import UpsertHabitLogRequest

router = APIRouter()


@router.put("/habits/{habit_id}/logs/{date}")
def upsert_habit_log(request_body: UpsertHabitLogRequest, habit_id: int, date: date, response: Response,
                     session: SessionDep):
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

def get_longest_perfect_streak(logs):
    if not logs or len(logs) < 2:
        return 0

    # Step 1: Group records by date and check for perfect days
    perfect_dates = [
        log.created_at.date()  # Single conversion: datetime → date
        for log in logs
        if log.completion_percentage == 100
    ]

    # If less than 2 perfect days exist, no streak possible
    if len(perfect_dates) < 2:
        return 0

    # Step 2: Sort perfect dates
    sorted_perfect_dates = sorted(perfect_dates)

    # Step 3: Find longest consecutive sequence
    max_streak = 0
    current_streak = 1
    for i in range(1, len(sorted_perfect_dates)):
        # Check if dates are consecutive (1 day apart)
        if (sorted_perfect_dates[i] - sorted_perfect_dates[i - 1]).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            # Reset streak on gap
            current_streak = 1

    # Return streak only if it's 2 or more days
    return max_streak if max_streak >= 2 else 0

def get_longest_active_streak(logs):
    if not logs or len(logs) < 2:
        return 0

    active_dates = [log.created_at.date() for log in logs]
    sorted_active_dates = sorted(active_dates)
    max_streak = 0
    current_streak = 1

    for i in range(1, len(sorted_active_dates)):
        if (sorted_active_dates[i] - sorted_active_dates[i - 1]).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    return max_streak if max_streak >= 2 else 0

def create_monthly_summary(month_logs):
    daily_progress = []
    monthly_summary = {
        "active_days": 0,
        "longest_active_streak": 0,
        "perfect_days": 0,
        "longest_perfect_streak": 0,
        "total_completed": 0
    }

    perfect_days = 0
    total_completed = 0
    goal_unit = month_logs[0].goal_unit
    for i, log in enumerate(month_logs):
        daily_progress.append({
            "date": log.created_at.strftime("%m/%d/%Y"),
            "completion_percentage": log.completion_percentage
        })

        if log.completion_percentage == 100:
            perfect_days += 1

        total_completed += log.progress_value

    monthly_summary["active_days"] = len(month_logs)
    monthly_summary["longest_active_streak"] = get_longest_active_streak(month_logs)
    monthly_summary["perfect_days"] = perfect_days
    monthly_summary["longest_perfect_streak"] = get_longest_perfect_streak(month_logs)
    monthly_summary["total_completed"] = f"{total_completed} {goal_unit}"
    return daily_progress, monthly_summary

def calculate_yearly_totals(monthly_summaries: List[Dict]) -> Tuple[int, int]:
    """
    Function that calculates the yearly perfect_days and total_completed
    :param monthly_summaries: list that contains monthly summaries to be processed
    """
    yearly_perfect_days = 0
    yearly_total_completed = 0

    for summary in monthly_summaries:
        yearly_perfect_days += summary["perfect_days"]
        # TODO: research how to keep consistency with the float thing here
        yearly_total_completed += float(summary["total_completed"].split()[0])

    return yearly_perfect_days, yearly_total_completed

@router.get("/habits/{habit_id}/year/{year}")
def get_yearly_summary(habit_id: int, year: int, session: SessionDep):
    yearly_habit_logs_statement = select(HabitLogs).where(HabitLogs.habit_fk == habit_id).where(
        func.year(HabitLogs.created_at) == year).order_by(HabitLogs.created_at)
    yearly_habit_logs = session.exec(yearly_habit_logs_statement).all()

    response = {
        "monthly_data": {},
        "yearly_summary": {}
    }

    if len(yearly_habit_logs) == 0:
        return response

    logs_by_month = {i: [] for i in range(1, 13)}
    num_to_month = {
        1: "january",
        2: "february",
        3: "march",
        4: "april",
        5: "may",
        6: "june",
        7: "july",
        8: "august",
        9: "september",
        10: "october",
        11: "november",
        12: "december"
    }
    for log in yearly_habit_logs:
        month_number = log.created_at.month
        logs_by_month[month_number].append(log)

    monthly_data = defaultdict(dict)
    for i in range(1, 13):
        if len(logs_by_month[i]) > 0:
            daily_progress, monthly_summary = create_monthly_summary(logs_by_month[i])
            monthly_data[num_to_month[i]]["daily_progress"] = daily_progress
            monthly_data[num_to_month[i]]["monthly_summary"] = monthly_summary
    response["monthly_data"] = monthly_data

    # Create yearly summary
    monthly_summaries = []
    for i in range(1, 13):
        if num_to_month[i] in monthly_data:
            monthly_summaries.append(monthly_data[num_to_month[i]]["monthly_summary"])
    perfect_days_in_year, total_completed_in_year = calculate_yearly_totals(monthly_summaries)
    yearly_summary = {
        "active_days": len(yearly_habit_logs),
        "longest_active_streak": get_longest_active_streak(yearly_habit_logs),
        "perfect_days": perfect_days_in_year,
        "longest_perfect_streak": get_longest_perfect_streak(yearly_habit_logs),
        "total_completed": f"{total_completed_in_year} {yearly_habit_logs[0].goal_unit}"
    }
    response["yearly_summary"] = yearly_summary
    return response
