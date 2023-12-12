from fastapi import Query
from pydantic import BaseModel

from services.embeddings import EmbeddingType


class CompletionResponse(BaseModel):
    suggestions: list[str]


class Movie(BaseModel):
    score: float
    title: str
    tmbdId: int | None = None
    item_id: int
    year: int
    overview: str
    runtime: str
    genres: list[str] | None = None
    vote_average: float | None = None
    popularity: float | None = None
    director: str | None = None
    protagonists: list[str]
    backdrop_path: str | None = None
    poster_path: str | None = None


class MoviesResponse(BaseModel):
    total: int
    size: int
    offset: int
    did_you_mean: str | None = None
    did_you_mean_html: str | None = None
    movies: list[Movie]


class MovieSearchParams:
    def __init__(
        self,
        offset: int = 0,
        size: int = 50,
        search: str = "",
        min_year: int | None = None,
        max_year: int | None = None,
        genres_in: list[str] = Query(default=[]),
        genres_out: list[str] = Query(default=[]),
        min_rating: int | None = None,
        include_suggestions: bool = False,
        emb_type: EmbeddingType = EmbeddingType.SYMMETRIC,
        semantic_search: bool = False
    ):
        self.offset = offset
        self.size = size
        self.search = search
        self.min_year = min_year
        self.max_year = max_year
        self.genres_in = genres_in
        self.genres_out = genres_out
        self.min_rating = min_rating
        self.include_suggestions = include_suggestions
        self.emb_type = emb_type
        self.semantic_search = semantic_search
