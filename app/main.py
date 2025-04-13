from fastapi import FastAPI, Depends
# from .routers import habits
from typing import Annotated, List
from sqlmodel import Session, select
from .db.database import engine
from .models.habits_model import Habits # TODO: Delete this later

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# Might need to create the db tables on startup. Not sure yet

app = FastAPI()


# app.include_router(habits.router)

@app.get("/")
def read_root():
    return {"Hello": "World!"}

@app.get("/habits-db-test")
def get_habits_from_db(session: SessionDep) -> List[Habits]:
    habits = session.exec(select(Habits)).all()
    return habits