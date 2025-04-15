from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Habits(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color_hex: Optional[str] = None
    is_bad_habit: bool
    repeat_type: str
    repeat_config: Optional[str] = None
    is_archived: bool
    is_check_only: bool
    start_date: datetime
    end_date: Optional[datetime] = None
    display_order: Optional[int] = None
    goal: str
    goal_is_time: bool
    created_at: datetime
    updated_at: datetime