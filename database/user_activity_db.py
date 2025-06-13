from prisma.models import UserSearchHistory, movies as Movies, UserFavorites
from typing import Optional, Tuple, List

def add_search_history(user_id: int, query: str) -> Tuple[Optional[dict], Optional[str]]:
    try:
        search_history = UserSearchHistory.prisma().create({
            "data": {
                "userId": user_id,
                "query": query
            }
        })
        return search_history, None
    except Exception as e:
        return None, str(e)

def get_search_history(user_id: int) -> Tuple[Optional[List[dict]], Optional[str]]:
    try:
        search_history = UserSearchHistory.prisma().find_many(
            where={"userId": user_id},
            order={"timestamp": "desc"}
        )
        return search_history, None
    except Exception as e:
        return None, str(e)

def delete_search_history(history_id: int, user_id: int) -> Tuple[Optional[dict], Optional[str]]:
    try:
        history = UserSearchHistory.prisma().find_unique(
            where={"id": history_id}
        )
        
        if not history or history.userId != user_id:
            return None, "Search history not found"
        
        deleted = UserSearchHistory.prisma().delete(
            where={"id": history_id}
        )
        return deleted, None
    except Exception as e:
        return None, str(e)

def search_movies(query: str) -> Tuple[Optional[List[dict]], Optional[str]]:
    try:
        movies = Movies.prisma().find_many(
            where={
                "title": {
                    "contains": query
                }
            },
            take=20 
        )
        return movies, None
    except Exception as e:
        return None, str(e)

def add_favorite(user_id: int, movie_id: int) -> Tuple[Optional[dict], Optional[str]]:
    try:
        movie = Movies.prisma().find_unique(
            where={"movie_id": movie_id}
        )
        if not movie:
            return None, "Movie not found"
        
        favorite = UserFavorites.prisma().create({
            "data": {
                "userId": user_id,
                "movieId": movie_id
            }
        })
        return favorite, None
    except Exception as e:
        return None, str(e)

def get_favorites(user_id: int) -> Tuple[Optional[List[dict]], Optional[str]]:
    try:
        favorites = UserFavorites.prisma().find_many(
            where={"userId": user_id},
            include={"movie": True},
            order={"timestamp": "desc"}
        )
        return favorites, None
    except Exception as e:
        return None, str(e)

def remove_favorite(user_id: int, movie_id: int) -> Tuple[Optional[dict], Optional[str]]:
    try:
        favorite = UserFavorites.prisma().find_unique(
            where={
                "userId_movieId": {
                    "userId": user_id,
                    "movieId": movie_id
                }
            }
        )
        
        if not favorite:
            return None, "Favorite not found"
        
        deleted = UserFavorites.prisma().delete(
            where={
                "userId_movieId": {
                    "userId": user_id,
                    "movieId": movie_id
                }
            }
        )
        return deleted, None
    except Exception as e:
        return None, str(e)
