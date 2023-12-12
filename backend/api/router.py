from fastapi import APIRouter, Depends
from typing import Any

from api.schemas import CompletionResponse, Movie, MovieSearchParams, MoviesResponse
from services.search import ESManager, SearchManager


router = APIRouter()

sm = SearchManager()
em = ESManager()


@router.get("/movies", response_model=MoviesResponse)
def traditional_movie_search(params: MovieSearchParams = Depends()) -> Any:
    if params.semantic_search:
        movies, total, did_you_mean, did_you_mean_html = sm.execute_hybrid_search(params, em)
    else:
        movies, total, did_you_mean, did_you_mean_html = sm.execute_traditional_search(params, em)
    return MoviesResponse(
        total=total,
        size=params.size,
        offset=params.offset,
        did_you_mean=did_you_mean,
        did_you_mean_html=did_you_mean_html,
        movies=movies,
    )


@router.get("/completion", response_model=CompletionResponse)
def get_completion_suggestions(query: str) -> Any:
    suggestions = sm.get_completion_suggestions(query, em)
    return CompletionResponse(suggestions=suggestions)
