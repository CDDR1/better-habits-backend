from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, Session
from ..config import settings

# URL Structure: "mysql+pymysql://<username>:<password>@<host>:<port>/<database_name>"
DATABASE_URL = f"mysql+pymysql://{settings.db_username}:{settings.db_password}@{settings.db_dev_host}:{settings.db_port}/{settings.db_name}"

engine = create_engine(DATABASE_URL)

SessionLocal = Session(bind=engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]