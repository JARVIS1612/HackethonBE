import faiss
import numpy as np
import json
from datetime import datetime
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from database.movie_db import get_movie_by_id_from_db
from Modules.movies import format_movie_data

load_dotenv()
POSTER_PATH_URL = os.getenv("POSTER_PATH_URL")

class HybridVectorStore:
    def __init__(self):
        # Initialize the embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize FAISS index
        self.dimension = 384  # dimension of all-MiniLM-L6-v2
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Store movie metadata and mapping
        self.movie_ids = []  # Maps FAISS indices to movie IDs
        self.movie_metadata = {}  # Stores movie details
        
        # Load existing data if available
        self.load_state()
    
    def add_movies(self, movies: List[Dict]):
        """Add movies to the vector store"""
        # Prepare texts for embedding
        texts = [f"{m['title']} {m.get('description', '')}" for m in movies]
        
        # Generate embeddings
        embeddings = self.model.encode(texts)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        for i, movie in enumerate(movies):
            movie_id = movie.get('id', str(len(self.movie_ids)))
            self.movie_ids.append(movie_id)
            self.movie_metadata[movie_id] = movie
        
        # Save state
        self.save_state()
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar movies"""
        # Generate query embedding
        query_embedding = self.model.encode([query])
        
        # Search in FAISS
        distances, indices = self.index.search(
            query_embedding.astype('float32'), 
            k
        )
        
        # Get results with metadata
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.movie_ids):
                movie_id = self.movie_ids[idx]
                movie_data = self.movie_metadata.get(movie_id, {})
             
                data, error = get_movie_by_id_from_db(movie_data.get("movie_id"))
                if data:
                    movie_data = format_movie_data(data)
                movie_data['similarity_score'] = float(1 / (1 + distances[0][i]))

                if movie_data.get("description"):
                    movie_data["overview"] = movie_data["description"]
                results.append(movie_data)
        
        return results
    
    def save_state(self):
        """Save the current state to disk"""
        # Save FAISS index
        faiss.write_index(self.index, "movie_embeddings.index")
        
        # Save metadata
        state = {
            'movie_ids': self.movie_ids,
            'movie_metadata': self.movie_metadata,
            'last_updated': datetime.now().isoformat()
        }
        
        with open("movie_vector_store.json", "w") as f:
            json.dump(state, f)
    
    def load_state(self):
        """Load state from disk"""
        try:
            # Only load if files exist
            if os.path.exists("movie_embeddings.index") and os.path.exists("movie_vector_store.json"):
                # Load FAISS index
                self.index = faiss.read_index("movie_embeddings.index")
                # Load metadata
                with open("movie_vector_store.json", "r") as f:
                    state = json.load(f)
                    self.movie_ids = state['movie_ids']
                    self.movie_metadata = state['movie_metadata']
            else:
                # Initialize new if no saved state
                self.index = faiss.IndexFlatL2(self.dimension)
                self.movie_ids = []
                self.movie_metadata = {}
        except Exception as e:
            # On any error, reinitialize
            self.index = faiss.IndexFlatL2(self.dimension)
            self.movie_ids = []
            self.movie_metadata = {} 