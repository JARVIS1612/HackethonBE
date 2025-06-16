# This file will contain functions for handling movie-related database operations.
from prisma.models import movies as PrismaMovies, actors as PrismaActors, genres as PrismaGenres, UserFavorites
from typing import List, Optional
from prisma import Prisma


def get_all_movies_from_db(
        page: int = 1, 
        page_size: int = 10, 
        genre_id: Optional[int] = None, 
        top_n_movies: Optional[int] = None
    ):
    """
    Get all movies with pagination and optional filtering
    """
    try:
        skip = (page - 1) * page_size
        
        # Build where clause
        where_clause = {}
        order_by_clause = []
        if genre_id:
            where_clause["movie_genres"] = {
                "some": {
                    "genre_id": genre_id
                }
            }
        
        # Get movies with related data
        movies = PrismaMovies.prisma().find_many(
            where=where_clause,
            skip=skip,
            take=page_size,
            order=order_by_clause,
            include={
                "movie_cast": {
                    "include": {
                        "actors": True
                    }
                },
                "movie_genres": {
                    "include": {
                        "genres": True
                    }
                }
            }
        )
        
        # Get total count
        total_count = PrismaMovies.prisma().count(where=where_clause)
        
        return movies, total_count, None
        
    except Exception as e:
        return None, 0, str(e)


def get_movie_by_id_from_db(movie_id: int):
    """
    Get a single movie by ID with all related data
    """
    try:
        movie = PrismaMovies.prisma().find_unique(
            where={"movie_id": movie_id},
            include={
                "movie_cast": {
                    "include": {
                        "actors": True
                    }
                },
                "movie_genres": {
                    "include": {
                        "genres": True
                    }
                }
            }
        )
        
        return movie, None
        
    except Exception as e:
        return None, str(e)


def get_movies_by_genre_from_db(genre_id: int, page: int = 1, page_size: int = 10):
    """
    Get movies filtered by genre
    """
    return get_all_movies_from_db(page=page, page_size=page_size, genre_id=genre_id)


def get_movies_by_actor_from_db(actor_id: int, page: int = 1, page_size: int = 10):
    """
    Get movies filtered by actor
    """
    try:
        skip = (page - 1) * page_size
        
        where_clause = {
            "movie_cast": {
                "some": {
                    "actor_id": actor_id
                }
            }
        }
        
        movies = PrismaMovies.prisma().find_many(
            where=where_clause,
            skip=skip,
            take=page_size,
            include={
                "movie_cast": {
                    "include": {
                        "actors": True
                    }
                },
                "movie_genres": {
                    "include": {
                        "genres": True
                    }
                }
            }
        )
        
        total_count = PrismaMovies.prisma().count(where=where_clause)
        
        return movies, total_count, None
        
    except Exception as e:
        return None, 0, str(e)


def get_all_genres_from_db():
    """
    Get all available genres
    """
    try:
        genres = PrismaGenres.prisma().find_many()
        return genres, None
        
    except Exception as e:
        return None, str(e)

def get_top_n_movies(n, genre_id):
    try:
        where_clause = {}
        where_clause['revenue'] = {
            'gt': 0
        }

        if genre_id:
            where_clause['genre_id'] = genre_id
        
        order_by_clause = [
            {
                'rating': 'desc',
            },
            {
                'release_date': 'desc',
            },
            {
                'revenue': 'desc',
            },
        ]

        movies = PrismaMovies.prisma().find_many(
                where=where_clause,
                skip=0,
                take=n,
                order=order_by_clause
            )
        
        total_count = PrismaMovies.prisma().count(where=where_clause)
            
        return movies, total_count, None
    except Exception as e:
        return None, str(e)
    
def get_favorites_movies(
    page: int = 1,
    page_size: int = 10,
    genre_id: Optional[int] = None,
    current_user_id: int = None
) -> tuple[List[dict], int, Optional[str]]:
    try:
        skip = (page - 1) * page_size

        # Build the filter condition
        filter_condition = {
            "userId": current_user_id,
            "movie": {
                "genres": {
                    "some": {
                        "genre_id": genre_id
                    }
                } if genre_id else {}
            } if genre_id else {}
        }

        # Fetch paginated favorite movies
        favorites = UserFavorites.prisma().find_many(
            where=filter_condition,
            order={"timestamp": "desc"},
            skip=skip,
            take=page_size,
            include={"movie": True}
        )

        # Fetch count
        total_count = UserFavorites.prisma().count(where=filter_condition)

        # Extract movies from favorites
        movies = [fav.movieId for fav in favorites]

        return movies, total_count, None

    except Exception as e:
        return [], 0, str(e)