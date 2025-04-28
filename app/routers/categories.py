from typing import List

from fastapi import APIRouter
from sqlmodel import select

from ..db.database import SessionDep
from ..models.models import Habits, HabitLogs, Categories
from ..schemas.schemas import CreateCategoryRequest, UpdateCategoryRequest, DeleteCategoryResponse

router = APIRouter()

@router.get("/users/{user_id}/categories")
def get_categories_for_user(user_id: int, session: SessionDep) -> List[Categories]:
    statement = select(Categories).where(Categories.user_fk == user_id)
    categories = session.exec(statement).all()
    return categories

@router.post("/categories")
def create_category(category: CreateCategoryRequest, session: SessionDep) -> Categories:
    new_category = Categories(**category.model_dump())
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category

@router.patch("/categories/{category_id}")
def update_category(category_id: int, updated_category: UpdateCategoryRequest, session: SessionDep) -> Categories:
    category = session.exec(select(Categories).where(Categories.id == category_id)).one()
    updated_category_dict = updated_category.model_dump(exclude_unset=True)
    for key, value in updated_category_dict.items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, session: SessionDep) -> DeleteCategoryResponse:
    statement = select(Categories).where(Categories.id == category_id)
    category = session.exec(statement).one()
    session.delete(category)
    session.commit()

    # confirm category was deleted
    deleted_category = session.exec(statement).first()
    if deleted_category is not None:
        # TODO: Raise an exception
        pass

    response = DeleteCategoryResponse(is_success=True)
    return response