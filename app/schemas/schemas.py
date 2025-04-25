from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color_hex: Optional[str] = None
    is_bad_habit: bool
    repeat_type: str
    repeat_config: Optional[str] = None
    is_check_only: bool
    start_date: datetime
    end_date: Optional[datetime] = None
    goal: Optional[str] = None
    goal_is_time: bool
    user_fk: int
