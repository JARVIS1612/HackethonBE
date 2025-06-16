from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from Modules.hybrid_vector_store import HybridVectorStore
from Helpers.jwt_helpers import get_current_user
from database.movie_db import get_movie_by_id_from_db
from Modules.movies import format_movie_data
from database.user_activity_db import add_search_history, get_search_history
from database.movie_db import get_favorites_movies
import requests
stopwords_list = requests.get("https://gist.githubusercontent.com/rg089/35e00abf8941d72d419224cfd5b5925d/raw/12d899b70156fd0041fa9778d657330b024b959c/stopwords.txt").content
STOPWORDS = set(stopwords_list.decode().splitlines())


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
        
        # Store search history
        search_history, history_error = add_search_history(current_user.id, query)
        if history_error:
            print(f"Error recording search history: {history_error}")
            
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
    current_user: Dict = Depends(get_current_user),
    k: int = 5
):
    try:
        # Construct weighted query with proper formatting and null checks
        query_parts = []
        
        # Add location with lower weight
        if current_user.location:
            query_parts.append(f"location:{current_user.location}")
            
        # Add genres with higher weight (repeat twice for emphasis)
        if current_user.genres:
            genres = current_user.genres.split(',') if isinstance(current_user.genres, str) else current_user.genres
            for genre in genres:
                query_parts.append(f"genre:{genre.strip()}")
                query_parts.append(f"genre:{genre.strip()}")  # Double weight for genres
                
        # Add languages
        if current_user.languages:
            languages = current_user.languages.split(',') if isinstance(current_user.languages, str) else current_user.languages
            for language in languages:
                query_parts.append(f"language:{language.strip()}")
        
        temp_query = " ".join(query_parts) if query_parts else "popular movies"  # Fallback if no preferences
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
    

@vector_search.get("/recommendBasedOnHistory")
async def recommend_movies_based_on_history(
    current_user: Dict = Depends(get_current_user),
    k: int = 5
):
    try:
        # Get user's recent search history
        search_history, error = get_search_history(current_user.id)
        if error:
            raise HTTPException(status_code=500, detail=f"Error fetching search history: {error}")
            
        if not search_history:
            return {
                "success": True,
                "data": [],
                "message": "Recommendations generated successfully based on search history"
            }
            
        # Combine recent search queries with weights (more recent searches have higher weight)
        query_parts = []
        for i, history in enumerate(search_history[:5]):  # Use last 5 searches
            weight = 5 - i  # More recent searches get higher weight
            query_parts.extend([history.query] * weight)
        
        # Create the final query
        temp_query = " ".join(query_parts)
        
        # Get recommendations using the combined query
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
            "message": "Recommendations generated successfully based on search history"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
@vector_search.get("/recommendBasedOnLikedMovies")
async def recommend_movies_based_on_liked_movies(
    current_user: Dict = Depends(get_current_user),
    k: int = 5
):
    try:
        # Get user's favorite movies
        favorite_movies, total_count, error = get_favorites_movies(
            page=1,
            page_size=10,  # Get last 10 favorite movies
            current_user_id=current_user.id
        )
        
        if error:
            raise HTTPException(status_code=500, detail=f"Error fetching favorite movies: {error}")
            
        if not favorite_movies:
            return {
                "success": True,
                "data": [],
                "message": "No favorite movies found to generate recommendations"
            }
            
        # Build query based on favorite movies' characteristics
        query_parts = []
        
        # Process each favorite movie
        for movie in favorite_movies:
            # Add movie title with high weight
            if movie.get("title"):
                query_parts.extend([movie["title"]] * 3)  # Triple weight for titles
                
            # Get detailed movie data to access genres and cast
            movie_data, error = get_movie_by_id_from_db(movie.get("movie_id"))
            if movie_data:
                # Add genres
                for genre_relation in movie_data.movie_genres or []:
                    if genre_relation.genres and genre_relation.genres.genre_name:
                        query_parts.extend([f"genre:{genre_relation.genres.genre_name}"] * 2)  # Double weight for genres
                
                # Add movie description
                if movie_data.overview:
                    # Split description into words and filter out stopwords
                    words = [word.lower() for word in movie_data.overview.split() 
                            if word.lower() not in STOPWORDS and len(word) > 2]
                    # Add each word with single weight
                    query_parts.extend(words)
        
        # Create the final query
        temp_query = " ".join(query_parts)
        
        # Get recommendations using the combined query
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
            "message": "Recommendations generated successfully based on favorite movies"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 