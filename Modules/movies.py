from fastapi import APIRouter, Query, Depends
from fastapi.responses import FileResponse
from typing import Optional
from Models.movie_list_models import MovieListResponse, MovieDetailResponse
from database.movie_db import (
    get_all_movies_from_db, 
    get_movie_by_id_from_db, 
    get_movies_by_genre_from_db,
    get_favorites_movies,
    get_all_genres_from_db,
    get_top_n_movies
)
from Helpers.custom_response import unified_response
import os
from dotenv import load_dotenv

from database.user_activity_db import add_search_history, search_movies
from Modules.authentication import get_current_user
# Get the project root directory (2 levels up from this file)
load_dotenv()
POSTER_PATH_URL = os.getenv("POSTER_PATH_URL")

movies = APIRouter(prefix="/movie", tags=["Movies"])

def format_movie_data(movie_data):
    if not movie_data:
        return None
    
    cast = []
    for cast_member in movie_data.movie_cast or []:
        cast.append({
            "actor_id": cast_member.actor_id,
            "character_name": cast_member.character_name,
            "credit_order": cast_member.credit_order,
            "credit_id": cast_member.credit_id,
            "actor": {
                "actor_id": cast_member.actors.actor_id,
                "actor_name": cast_member.actors.actor_name,
                "gender": cast_member.actors.gender,
                "profile_path": cast_member.actors.profile_path
            } if cast_member.actors else None
        })
    
    genres = []
    for genre_relation in movie_data.movie_genres or []:
        genres.append({
            "genre_id": genre_relation.genre_id,
            "genre": {
                "genre_id": genre_relation.genres.genre_id,
                "genre_name": genre_relation.genres.genre_name,
                "genre_poster":POSTER_PATH_URL+"/genres/"+str(genre_relation.genres.genre_name)+".gif"
            } if genre_relation.genres else None
        })
    return {
        "movie_id": movie_data.movie_id,
        "title": movie_data.title,
        "poster_path": POSTER_PATH_URL+"/posters/"+str(movie_data.movie_id)+".jpg",
        "release_date": movie_data.release_date.isoformat() if movie_data.release_date else None,
        "budget": movie_data.budget,
        "revenue": movie_data.revenue,
        "runtime": movie_data.runtime,
        "overview": movie_data.overview,
        "rating": movie_data.rating,
        "cast": cast,
        "genres": genres
    }

@movies.get("/", response_model=MovieListResponse)
async def get_all_movies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of movies per page"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    top_n_movies: Optional[int] = Query(None, description="Filter by top N movies"),
):
    movies_data, total_count, error = get_all_movies_from_db(
        page=page, 
        page_size=page_size, 
        genre_id=genre_id, 
        top_n_movies=top_n_movies
    )
    
    if error:
        return unified_response(False, f"Error fetching movies: {error}", status_code=500)
    
    formatted_movies = []
    for movie in movies_data:
        formatted_movie = format_movie_data(movie)
        if formatted_movie:
            formatted_movies.append(formatted_movie)
    
    response_data = {
        "movies": formatted_movies,
        "total_count": total_count,
        "page": page,
        "page_size": page_size
    }
    
    return unified_response(True, "Movies fetched successfully", data=response_data)

@movies.get("/filter")
def filter_movies_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of movies per page"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    top_n_movies: Optional[int] = Query(None, description="Filter by top N movies"),
    favourits_movies: Optional[bool] = Query(None, description="Filter by favourits movies"),
    current_user: dict = Depends(get_current_user)
    ):
    """Filter movies by genre ID or top N movies"""
    movies_data = []

    if top_n_movies:
        movies_data, total_count, error = get_top_n_movies(
            n=top_n_movies, genre_id=genre_id
        )
    
    elif favourits_movies:
        movies_data, total_count, error = get_favorites_movies(
            page=page,
            page_size=page_size,
            genre_id=genre_id,
            current_user_id=current_user.get("id")
        )
    if error:
        return unified_response(False, f"Error fetching movies: {error}", status_code=500)
    
    formatted_movies = []
    for movie in movies_data:
        formatted_movie = format_movie_data(movie)
        if formatted_movie:
            formatted_movies.append(formatted_movie)
    
    response_data = {
        "movies": formatted_movies,
        "total_count": total_count,
        "page": page,
        "page_size": page_size
    }
    
    return unified_response(True, "Movies fetched successfully", data=response_data)

@movies.get("/search")
def search_movies_endpoint(query: str, current_user: dict = Depends(get_current_user)):
    movies, error = search_movies(query)
    if error:
        return unified_response(False, f"Error searching movies: {error}", status_code=500)
    
    search_history, history_error = add_search_history(current_user["id"], query)
    if history_error:
        print(f"Error recording search history: {history_error}")
    
    movies_res = []
    for m in movies:
        movies_res.append(format_movie_data(m))

    return unified_response(True, "Search completed successfully", data=movies_res)

@movies.get("/{movie_id}", response_model=MovieDetailResponse)
async def get_movie_by_id(movie_id: int):
    """Get detailed information about a specific movie"""
    movie_data, error = get_movie_by_id_from_db(movie_id)
    
    if error:
        return unified_response(False, f"Error fetching movie: {error}", status_code=500)
    
    if not movie_data:
        return unified_response(False, "Movie not found", status_code=404)
    
    formatted_movie = format_movie_data(movie_data)
    
    return unified_response(True, "Movie details fetched successfully", data={"movie": formatted_movie})

@movies.get("/genre/{genre_id}")
async def get_movies_by_genre(
    genre_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of movies per page")
):
    """Get movies filtered by genre"""
    movies_data, total_count, error = get_movies_by_genre_from_db(
        genre_id=genre_id,
        page=page,
        page_size=page_size
    )
    
    if error:
        return unified_response(False, f"Error fetching movies by genre: {error}", status_code=500)
    
    formatted_movies = []
    for movie in movies_data:
        formatted_movie = format_movie_data(movie)
        if formatted_movie:
            formatted_movies.append(formatted_movie)
    
    response_data = {
        "movies": formatted_movies,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "genre_id": genre_id,
    }
    
    return unified_response(True, f"Movies for genre {genre_id} fetched successfully", data=response_data)

@movies.get("/genres/all")
async def get_all_genres():
    """Get all available genres"""
    genres_data, error = get_all_genres_from_db()
    
    if error:
        return unified_response(False, f"Error fetching genres: {error}", status_code=500)
    
    formatted_genres = []
    for genre in genres_data:
        formatted_genres.append({
            "genre_id": genre.genre_id,
            "genre_name": genre.genre_name,
            "genre_poster":POSTER_PATH_URL+"/genres/"+str(genre.genre_name)+".gif"
        })
    
    return unified_response(True, "Genres fetched successfully", data={"genres": formatted_genres})
