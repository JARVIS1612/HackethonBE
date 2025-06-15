import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid
import asyncio

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

def process_movies():
    # Read movies from movie_details.json
    with open('movie_details.json', 'r') as f:
        movies = json.load(f)
    
    # Process each movie
    for movie in movies:
        # Create text for embedding
        text = f"Title: {movie['title']}. Description: {movie['description']}"
        
        # Generate embedding
        embedding = model.encode(text)
        
        # Generate a UUID for the point ID
        point_id = str(uuid.uuid4())
        
        # Upload to Qdrant
        qdrant_client.upsert(
            collection_name="movies",
            points=[
                models.PointStruct(
                    id=point_id,  # Use a UUID for each movie
                    vector=embedding.tolist(),
                    payload=movie
                )
            ]
        )
        print(f"Processed: {movie['title']}")

if __name__ == "__main__":
    process_movies()
    print("All movies have been processed and uploaded to Qdrant!") 