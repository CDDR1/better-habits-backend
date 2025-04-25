from fastapi import FastAPI
from .routers import habits



app = FastAPI()


app.include_router(habits.router)

@app.get("/")
def read_root():
    return {"Hello": "World!"} 