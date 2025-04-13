from fastapi import APIRouter

router = APIRouter()


@router.get("/habits", tags=["habits"])
async def read_users():
    return [{"habit_name": "Practice guitar"}, {"habit_name": "Read a book"}]