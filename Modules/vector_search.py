from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from Modules.hybrid_vector_store import HybridVectorStore
from Helpers.jwt_helpers import get_current_user

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