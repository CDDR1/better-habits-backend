from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


# //////////////////////////////////////// REQUESTS ////////////////////////////////////////
class UpsertHabitRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color_hex: Optional[str] = None
    is_bad_habit: Optional[bool] = None
    repeat_type: Optional[str] = None
    repeat_config: Optional[str] = None
    is_check_only: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    goal_value: Optional[int] = None
    goal_unit: Optional[str] = None
    goal_is_time: Optional[bool] = None
    user_fk: Optional[int] = None

class UpdateHabitCategoriesRequest(BaseModel):
    category_ids: List[int]

class ReorderHabit(BaseModel):
    id: int
    display_order: int

class ReorderHabitsRequest(BaseModel):
    habits_to_reorder: List[ReorderHabit]

class CreateCategoryRequest(BaseModel):
    name: str
    icon: Optional[str] = None
    user_fk: int

class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None

class UpsertHabitLogRequest(BaseModel):
    progress_value: float
    note: str
    goal_value: Optional[int] = None
    goal_unit: Optional[str] = None
    completion_percentage: float


# //////////////////////////////////////// RESPONSES ////////////////////////////////////////
class DeleteHabitResponse(BaseModel):
    is_success: bool

class ReorderHabitsResponse(BaseModel):
    is_success: bool

class DeleteCategoryResponse(BaseModel):
    is_success: bool
