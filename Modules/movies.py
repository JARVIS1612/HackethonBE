
from fastapi import APIRouter

movies = APIRouter(prefix="/movie", tags=["Auth"])

@movies.get("/")
async def get_all_movies():
    return {"message": "This is a list of all movies"}

