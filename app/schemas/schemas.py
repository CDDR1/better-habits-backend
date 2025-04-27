from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class UpsertHabit(BaseModel):
    name: str = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color_hex: Optional[str] = None
    is_bad_habit: bool = None
    repeat_type: str = None
    repeat_config: Optional[str] = None
    is_check_only: bool = None
    start_date: datetime = None
    end_date: Optional[datetime] = None
    goal: Optional[str] = None
    goal_is_time: bool = None
    user_fk: int = None
