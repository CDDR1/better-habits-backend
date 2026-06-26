from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, Session

from ..auth import CurrentUser
from ..db.database import SessionDep
from ..models.models import Categories, Habits
from ..schemas.schemas import CreateCategoryRequest, UpdateCategoryRequest

router = APIRouter(prefix="/categories", tags=["Categories"])


def _get_owned_category(category_id: int, user_id: str, session: Session) -> Categories:
    category = session.exec(
        select(Categories).where(Categories.id == category_id, Categories.user_id == user_id)
    ).one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("", summary="List categories")
def list_categories(user_id: CurrentUser, session: SessionDep) -> List[Categories]:
    """Return every category owned by the current user."""
    return session.exec(select(Categories).where(Categories.user_id == user_id)).all()


@router.post("", summary="Create a category", status_code=status.HTTP_201_CREATED)
def create_category(request: CreateCategoryRequest, user_id: CurrentUser, session: SessionDep) -> Categories:
    """Create a new category for the current user."""
    new_category = Categories(**request.model_dump(), user_id=user_id)
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category


@router.patch("/{category_id}", summary="Update a category")
def update_category(category_id: int, request: UpdateCategoryRequest, user_id: CurrentUser, session: SessionDep) -> Categories:
    """Partial update. Only fields present in the body are changed."""
    category = _get_owned_category(category_id, user_id, session)

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    category.updated_at = datetime.now()

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}", summary="Delete a category", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, user_id: CurrentUser, session: SessionDep) -> None:
    """Delete a category. Any habits that referenced it have their `category_id` set to NULL
    so they aren't orphaned."""
    category = _get_owned_category(category_id, user_id, session)

    affected_habits = session.exec(
        select(Habits).where(Habits.category_id == category_id, Habits.user_id == user_id)
    ).all()
    for habit in affected_habits:
        habit.category_id = None
        session.add(habit)

    session.delete(category)
    session.commit()
