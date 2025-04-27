from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

class UpsertHabitRequest(BaseModel):
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
    goal_value: Optional[int] = None
    goal_unit: Optional[str] = None
    goal_is_time: bool = None
    user_fk: int = None

class UpdateHabitCategoriesRequest(BaseModel):
    category_ids: List[int]

class DeleteHabitResponse(BaseModel):
    is_success: bool