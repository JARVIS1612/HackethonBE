from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from Models.movie_list_models import MovieListResponse, MovieDetailResponse, MovieModel, GenreModel
from database.movie_db import (
    get_all_movies_from_db, 
    get_movie_by_id_from_db, 
    get_movies_by_genre_from_db,
    get_movies_by_actor_from_db,
    get_all_genres_from_db
)
from Helpers.custom_response import unified_response
import os
from dotenv import load_dotenv

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
                "genre_name": genre_relation.genres.genre_name
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
    search: Optional[str] = Query(None, description="Search movies by title")
):
    movies_data, total_count, error = get_all_movies_from_db(
        page=page, 
        page_size=page_size, 
        genre_id=genre_id, 
        search=search
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
        "genre_id": genre_id
    }
    
    return unified_response(True, f"Movies for genre {genre_id} fetched successfully", data=response_data)


@movies.get("/actor/{actor_id}")
async def get_movies_by_actor(
    actor_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of movies per page")
):
    """Get movies filtered by actor"""
    movies_data, total_count, error = get_movies_by_actor_from_db(
        actor_id=actor_id,
        page=page,
        page_size=page_size
    )
    
    if error:
        return unified_response(False, f"Error fetching movies by actor: {error}", status_code=500)
    
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
        "actor_id": actor_id
    }
    
    return unified_response(True, f"Movies for actor {actor_id} fetched successfully", data=response_data)


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
            "genre_name": genre.genre_name
        })
    
    return unified_response(True, "Genres fetched successfully", data={"genres": formatted_genres})

