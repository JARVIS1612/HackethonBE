from fastapi import APIRouter, Depends, UploadFile, File
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from Helpers.custom_response import unified_response
from Modules.authentication import get_current_user
import json
import uuid

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Qdrant client
qdrant_client = QdrantClient(host="localhost", port=6333)

# Create collection if it doesn't exist
try:
    qdrant_client.get_collection("movies")
except Exception:
    qdrant_client.create_collection(
        collection_name="movies",
        vectors_config=models.VectorParams(
            size=384,  # Size of the vectors from all-MiniLM-L6-v2
            distance=models.Distance.COSINE
        )
    )

vector_search = APIRouter(prefix="/vector", tags=["Vector Search"])

@vector_search.post("/upload")
async def upload_movies(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload movies from a JSON file to Qdrant."""
    try:
        # Read and parse the JSON file
        content = await file.read()
        movies = json.loads(content)
        
        # Process each movie
        for movie in movies:
            # Create text for embedding
            text = f"Title: {movie['title']}. Description: {movie['overview']}"
            embedding = model.encode(text)
            
            # Generate a unique ID if movie_id is not present
            movie_id = movie.get('movie_id', str(uuid.uuid4()))
            
            # Upload to Qdrant
            qdrant_client.upsert(
                collection_name="movies",
                points=[
                    models.PointStruct(
                        id=movie_id,
                        vector=embedding.tolist(),
                        payload=movie
                    )
                ]
            )
        
        return unified_response(True, f"Successfully uploaded {len(movies)} movies")
    except Exception as e:
        return unified_response(False, f"Error uploading movies: {str(e)}")

@vector_search.post("/process")
async def process_movies(movies: List[Dict[str, Any]]):
    """Process and store movies in Qdrant."""
    for movie in movies:
        text = f"Title: {movie['title']}. Description: {movie['overview']}"
        embedding = model.encode(text)
        qdrant_client.upsert(
            collection_name="movies",
            points=[
                models.PointStruct(
                    id=movie['movie_id'],  # Use movie_id as the point ID
                    vector=embedding.tolist(),
                    payload=movie
                )
            ]
        )
    return unified_response(True, f"Successfully processed {len(movies)} movies")

@vector_search.post("/search")
async def search_movies(query: str, limit: int = 5, current_user: dict = Depends(get_current_user)):
    """Search for similar movies using a text query."""
    query_embedding = model.encode(query)
    search_result = qdrant_client.search(
        collection_name="movies",
        query_vector=query_embedding.tolist(),
        limit=limit
    )
    results = [hit.payload for hit in search_result]
    return unified_response(True, "Search completed successfully", data=results)

@vector_search.post("/recommend")
async def recommend_movies(query: str, limit: int = 5, current_user: dict = Depends(get_current_user)):
    """Recommend movies based on a user query."""
    query_embedding = model.encode(query)
    search_result = qdrant_client.search(
        collection_name="movies",
        query_vector=query_embedding.tolist(),
        limit=limit
    )
    results = [hit.payload for hit in search_result]
    return unified_response(True, "Recommendations generated successfully", data=results) 