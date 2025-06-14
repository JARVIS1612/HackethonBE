from fastapi import APIRouter, Depends
from Modules.authentication import get_current_user
from database.user_activity_db import (
    add_search_history,
    get_search_history,
    delete_search_history,
    search_movies,
    add_favorite,
    remove_favorite
)
from Helpers.custom_response import unified_response

router = APIRouter(prefix="/user-activity", tags=["User Activity"])

@router.get("/search")
def search_movies_endpoint(query: str, current_user: dict = Depends(get_current_user)):
    movies, error = search_movies(query)
    if error:
        return unified_response(False, f"Error searching movies: {error}", status_code=500)
    
    search_history, history_error = add_search_history(current_user["id"], query)
    if history_error:
        print(f"Error recording search history: {history_error}")
    
    return unified_response(True, "Search completed successfully", data=movies)

@router.get("/search-history")
def get_user_search_history(current_user: dict = Depends(get_current_user)):
    search_history, error = get_search_history(current_user["id"])
    if error:
        return unified_response(False, f"Error fetching search history: {error}", status_code=500)
    
    return unified_response(True, "Search history retrieved successfully", data=search_history)

@router.delete("/search-history/{history_id}")
def delete_user_search_history(history_id: int, current_user: dict = Depends(get_current_user)):
    deleted, error = delete_search_history(history_id, current_user["id"])
    if error:
        return unified_response(False, f"Error deleting search history: {error}", status_code=500)
    
    return unified_response(True, "Search history deleted successfully")

@router.post("/favorites/{movie_id}")
def add_movie_to_favorites(movie_id: int, current_user: dict = Depends(get_current_user)):
    favorite, error = add_favorite(current_user["id"], movie_id)
    if error:
        return unified_response(False, f"Error adding favorite: {error}", status_code=500)
    
    return unified_response(True, "Movie added to favorites", data=favorite)

@router.delete("/favorites/{movie_id}")
def remove_movie_from_favorites(movie_id: int, current_user: dict = Depends(get_current_user)):
    deleted, error = remove_favorite(current_user["id"], movie_id)
    if error:
        return unified_response(False, f"Error removing favorite: {error}", status_code=500)
    
    return unified_response(True, "Movie removed from favorites") 