from datetime import datetime, date
from typing import Optional

from sqlmodel import SQLModel, Field, UniqueConstraint


class Categories(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Habits(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    color_hex: str
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class HabitLogs(SQLModel, table=True):
    __tablename__ = "habit_logs"
    __table_args__ = (UniqueConstraint("habit_id", "completed_on", name="uq_habit_log_per_day"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habits.id", index=True)
    completed_on: date
    created_at: datetime = Field(default_factory=datetime.now)
