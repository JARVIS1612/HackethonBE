# This file will contain functions for handling movie-related database operations.
from prisma.models import movies as PrismaMovies, actors as PrismaActors, genres as PrismaGenres
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
):
    try:
        db = Prisma()
        db.connect()

        skip = (page - 1) * page_size

        genre_filter = f"AND mg.genre_id = {genre_id}" if genre_id else ""

        query = f"""
        SELECT DISTINCT m.*
        FROM movies m
        JOIN UserFavorites uf ON uf.movieId = m.movie_id
        LEFT JOIN movie_genres mg ON mg.movie_id = m.movie_id
        WHERE uf.userId = {current_user_id}
        {genre_filter}
        ORDER BY uf.timestamp DESC
        LIMIT {page_size} OFFSET {skip};
        """

        count_query = f"""
        SELECT COUNT(DISTINCT m.movie_id) AS total
        FROM movies m
        JOIN UserFavorites uf ON uf.movieId = m.movie_id
        LEFT JOIN movie_genres mg ON mg.movie_id = m.movie_id
        WHERE uf.userId = {current_user_id}
        {genre_filter};
        """

        movies = db.query_raw(query)
        print("---------", movies)
        count_result = db.query_raw(count_query)
        total_count = count_result[0]['total'] if count_result else 0

        return movies, total_count, None

    except Exception as e:
        return None, 0, str(e)