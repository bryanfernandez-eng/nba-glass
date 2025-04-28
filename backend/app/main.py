from fastapi import FastAPI 
from app.routes import players 


app = FastAPI(
    title = "NBA Data Analyst API",
    description = "API for NBA Data Analyst project",
    version = "0.1.0",
)

app.include_router(players.router)

@app.get("/") 
def read_root():
    return {"message": "Welcome to the NBA Data Analyst API!"}