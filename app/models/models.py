from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

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
    display_order: Optional[int] = None
    goal: str
    goal_is_time: bool
    created_at: datetime
    updated_at: datetime

    categories: List["Categories"] = Relationship(back_populates="habits", link_model=HabitsCategoriesLink)


class Categories(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    icon: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    habits: List["Habits"] = Relationship(back_populates="categories", link_model=HabitsCategoriesLink)


