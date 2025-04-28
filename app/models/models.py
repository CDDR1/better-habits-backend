from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Users(SQLModel, table=True):
    id: int = Field(primary_key=True)
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime


class HabitsCategoriesLink(SQLModel, table=True):
    __tablename__ = "habits_categories_link"

    habit_fk: int = Field(foreign_key="habits.id", primary_key=True)
    category_fk: int = Field(foreign_key="categories.id", primary_key=True)
    created_at: datetime
    updated_at: datetime


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
    display_order: int = None
    goal_value: Optional[int] = None
    goal_unit: Optional[str] = None
    goal_is_time: bool
    user_fk: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    categories: List["Categories"] = Relationship(back_populates="habits", link_model=HabitsCategoriesLink)


class Categories(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    icon: Optional[str] = None
    user_fk: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    habits: List["Habits"] = Relationship(back_populates="categories", link_model=HabitsCategoriesLink)


class HabitLogs(SQLModel, table=True):
    __tablename__ = "habit_logs"

    id: int = Field(primary_key=True)
    habit_fk: int = Field(foreign_key="habits.id")
    is_completed: bool = False
    due_date: datetime
    progress_value: Optional[str] = None
    note: Optional[str] = None
    goal_value: Optional[int] = None
    goal_unit: Optional[str] = None
    created_at: datetime
    updated_at: datetime