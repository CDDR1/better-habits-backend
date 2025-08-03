from fastapi import FastAPI
from app.routers import habits, categories, habit_logs



app = FastAPI()


app.include_router(habits.router)
app.include_router(categories.router)
app.include_router(habit_logs.router)

@app.get("/")
def read_root():
    return {"Hello": "World!"}