from typing import Optional

from pydantic import BaseModel


class CreateHabitRequest(BaseModel):
    name: str
    color_hex: str
    description: Optional[str] = None
    category_id: Optional[int] = None


class UpdateHabitRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color_hex: Optional[str] = None
    category_id: Optional[int] = None


class CreateCategoryRequest(BaseModel):
    name: str
    description: Optional[str] = None


class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
