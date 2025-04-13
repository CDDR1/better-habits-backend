from sqlmodel import SQLModel, Field
from typing import Optional

class Habits(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(..., nullable=False)
    description: Optional[str] = Field(None, nullable=True)
    is_completed: bool = Field(..., nullable=False)
