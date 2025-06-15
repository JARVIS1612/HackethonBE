from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from Modules.hybrid_vector_store import HybridVectorStore
from Helpers.jwt_helpers import get_current_user

vector_search = APIRouter(prefix="/vector", tags=["Vector Search"])
vector_store = HybridVectorStore()

@vector_search.post("/search")
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

@vector_search.post("/recommend")
async def recommend_movies(
    query: str,
    k: int = 5,
    current_user: Dict = Depends(get_current_user)
):
    try:
        results = vector_store.search(query, k)
        return {
            "success": True,
            "data": results,
            "message": "Recommendations generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@vector_search.post("/genre-recommendations")
async def get_genre_recommendations(
    genre: str,
    k: int = 5,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get movie recommendations based on genre.
    The search will look for movies that match the genre in their metadata.
    """
    try:
        # Create a query that emphasizes the genre
        query = f"movies in the {genre} genre"
        results = vector_store.search(query, k)
        
        # Filter results to ensure they have the requested genre
        genre_results = [
            movie for movie in results 
            if genre.lower() in [g.lower() for g in movie.get('genres', [])]
        ]
        
        # If we don't have enough genre-specific results, add more from the original results
        if len(genre_results) < k:
            remaining = k - len(genre_results)
            additional_results = [
                movie for movie in results 
                if movie not in genre_results
            ][:remaining]
            genre_results.extend(additional_results)
        
        return {
            "success": True,
            "data": genre_results,
            "message": f"Found {len(genre_results)} movies in the {genre} genre"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 