from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from Modules.hybrid_vector_store import HybridVectorStore
from Helpers.jwt_helpers import get_current_user
from database.movie_db import get_movie_by_id_from_db
from Modules.movies import format_movie_data

vector_search = APIRouter(prefix="/vector", tags=["Vector Search"])
vector_store = HybridVectorStore()

@vector_search.get("/search")
async def search_movies(
    query: str,
    k: int = 5,
    current_user: Dict = Depends(get_current_user)
):
    try:
        results = vector_store.search(query, k)
        return {
            "success": True,
            "data": results,
            "message": "Search completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@vector_search.post("/upload")
async def upload_movies(
    movies: List[Dict],
    current_user: Dict = Depends(get_current_user)
):
    try:
        vector_store.add_movies(movies)
        return {
            "success": True,
            "message": f"Successfully uploaded {len(movies)} movies"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@vector_search.post("/process")
async def process_movies(
    movies: List[Dict],
    current_user: Dict = Depends(get_current_user)
):
    try:
        vector_store.add_movies(movies)
        return {
            "success": True,
            "message": f"Successfully processed {len(movies)} movies"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@vector_search.get("/recommend")
async def recommend_movies(
    current_user: Dict = Depends(get_current_user)
):
    try:
        k = 5
        temp_query = f"{current_user.location} {current_user.genres} {current_user.languages}"        
        results = vector_store.search(temp_query, k)
        response = []
        for movie in results:
            data, error = get_movie_by_id_from_db(movie.get("movie_id"))
            if data:
                movie_data = format_movie_data(data)
                response.append(movie_data)
    
        return {
            "success": True,
            "data": response,
            "message": "Recommendations generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 