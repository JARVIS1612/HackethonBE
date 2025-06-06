from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class ActorModel(BaseModel):
    actor_id: int
    actor_name: Optional[str] = None
    gender: Optional[int] = None
    profile_path: Optional[str] = None


class GenreModel(BaseModel):
    genre_id: int
    genre_name: Optional[str] = None


class MovieCastModel(BaseModel):
    actor_id: int
    character_name: Optional[str] = None
    credit_order: Optional[int] = None
    credit_id: Optional[str] = None
    actor: Optional[ActorModel] = None


class MovieGenreModel(BaseModel):
    genre_id: int
    genre: Optional[GenreModel] = None


class MovieModel(BaseModel):
    movie_id: int
    title: Optional[str] = None
    poster_path: Optional[str] = None
    release_date: Optional[date] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    runtime: Optional[float] = None
    overview: Optional[str] = None
    rating: Optional[float] = None
    cast: Optional[List[MovieCastModel]] = []
    genres: Optional[List[MovieGenreModel]] = []


class MovieListResponse(BaseModel):
    movies: List[MovieModel]
    total_count: int
    page: int
    page_size: int


class MovieDetailResponse(BaseModel):
    movie: MovieModel
