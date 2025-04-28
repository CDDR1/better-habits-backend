from fastapi import FastAPI
from .routers import habits, categories



app = FastAPI()


app.include_router(habits.router)
app.include_router(categories.router)

@app.get("/")
def read_root():
    return {"Hello": "World!"}