from typing import Any

from elasticsearch_dsl import Q, Search

from api.schemas import MovieSearchParams
from services.embeddings import EmbeddingType, get_embedding_for_text
from services.search import ESManager


class SearchManager:
    def _serialize_es_results(self, es_result: dict) -> dict:
        return {
            "score": es_result["_score"],
            "tmbdId": es_result["_source"].get("tmbdId"),
            "item_id": es_result["_source"]["item_id"],
            "title": es_result["_source"]["title"],
            "year": es_result["_source"]["year"],
            "overview": es_result["_source"]["overview"],
            "runtime": es_result["_source"]["runtime"],
            "genres_names": es_result["_source"]["genres"],
            "vote_average": es_result["_source"].get("vote_average"),
            "popularity": es_result["_source"].get("popularity"),
            "director": es_result["_source"].get("director"),
            "protagonists": es_result["_source"].get("protagonists", []),
            "backdrop_path": es_result["_source"].get("backdrop_path"),
            "poster_path": es_result["_source"].get("poster_path"),
        }

    def _get_traditional_search(
        self, params: MovieSearchParams, em: ESManager
    ) -> Search:
        search = Search(using=em.es_client, index=em.index_name)
        multi_match_query = Q(
            "multi_match",
            query=params.search,
            fields=["title^2", "overview"],
            operator="and",
        )

        include_genre_filters = [Q("term", genres=genre) for genre in params.genres_in]
        exclude_genre_filter = [Q("term", genres=genre) for genre in params.genres_out]
        rating_filter = Q("range", vote_average={"gt": params.min_rating})
        year_range_filter = Q(
            "range", year={"gte": params.min_year, "lte": params.max_year}
        )

        search = search.query(
            "bool",
            must=[multi_match_query, rating_filter] + include_genre_filters,
            must_not=exclude_genre_filter,
            filter=year_range_filter,
        )
        return search

    def _get_knn_search(
        self,
        params: MovieSearchParams,
        k: int,
        num_candidates: int,
    ) -> dict:
        emb_type = params.emb_type
        query_vector = get_embedding_for_text(params.search, emb_type)
        embedding_field = ""
        if emb_type == EmbeddingType.ASYMMETRIC:
            embedding_field = "sbert_symmetric_embedding"
        elif emb_type == EmbeddingType.SYMMETRIC:
            embedding_field = "sbert_asymmetric_embedding"
        elif emb_type == EmbeddingType.OPENAI:
            embedding_field = "openai_embedding"

        es_filters: list[dict[str, Any]] = [
            {
                "range": {
                    "year": {"gte": params.min_year, "lte": params.max_year},
                }
            },
            {"range": {"vote_average": {"gt": params.min_rating}}},
        ]
        exclude_genre_filter = [
            {"term": {"genres": genre}} for genre in params.genres_out
        ]
        es_filters.append({"bool": {"must_not": exclude_genre_filter}})

        include_genre_filters = [
            {"term": {"genres": genre}} for genre in params.genres_in
        ]
        es_filters.append({"bool": {"must": include_genre_filters}})

        return {
            "knn": {
                "field": embedding_field,
                "query_vector": query_vector,
                "k": k,
                "num_candidates": num_candidates,
                # "similarity": 0.78,
                "filter": es_filters,
            }
        }

    def _get_did_you_mean_suggestion(self, query) -> dict:
        return {
            "did_you_mean": {
                "text": query,
                "phrase": {
                    "field": "title.trigram",
                    "collate": {
                        "query": {
                            "source": {
                                "match": {
                                    "title": {
                                        "query": "{{suggestion}}",
                                        "operator": "and",
                                    }
                                }
                            }
                        }
                    },
                    "highlight": {
                        "pre_tag": "<strong>",
                        "post_tag": "</strong>",
                    },
                },
            }
        }

    def execute_traditional_search(
        self,
        params: MovieSearchParams,
        em: ESManager,
    ) -> tuple[list[dict], int]:
        traditional_query = self._get_traditional_search(params, em).to_dict()
        response = em.es_client.search(
            index=em.index_name,
            query=traditional_query["query"],
            size=params.size,
            from_=params.offset,
            suggest=self._get_did_you_mean_suggestion(params.search)
            if params.include_suggestions
            else None,
        )
        total = response["hits"]["total"]["value"]
        results = [self._serialize_es_results(r) for r in response["hits"]["hits"]]
        try:
            did_you_mean = response["suggest"]["did_you_mean"][0]["options"][0]["text"]
            did_you_mean_html = response["suggest"]["did_you_mean"][0]["options"][0]["highlighted"]
        except:
            did_you_mean = None
            did_you_mean_html = None
        return results, total, did_you_mean, did_you_mean_html

    def execute_hybrid_search(
        self,
        params: MovieSearchParams,
        em: ESManager,
        knn_k: int = 80,
        knn_num_candidates: int = 120,
    ) -> tuple[list[dict], int]:
        knn_query = self._get_knn_search(params, knn_k, knn_num_candidates)
        traditional_query = self._get_traditional_search(params, em).to_dict()
        response = em.es_client.search(
            index=em.index_name,
            query=traditional_query["query"],
            knn=knn_query["knn"],
            size=params.size,
            from_=params.offset,
            suggest=self._get_did_you_mean_suggestion(params.search)
            if params.include_suggestions
            else None,
        )
        total = response["hits"]["total"]["value"]
        results = [self._serialize_es_results(r) for r in response["hits"]["hits"]]
        try:
            did_you_mean = response["suggest"]["did_you_mean"][0]["options"][0]["text"]
            did_you_mean_html = response["suggest"]["did_you_mean"][0]["options"][0]["highlighted"]
        except:
            did_you_mean = None
            did_you_mean_html = None
        return results, total, did_you_mean, did_you_mean_html

    def get_completion_suggestions(self, query: str, em: ESManager) -> list[str]:
        response = em.es_client.search(
            suggest={
                "complete": {
                    "text": query,
                    "completion": {
                        "field": "title_completion",
                        "fuzzy": {"fuzziness": 2},
                        "size": 10,
                    },
                }
            },
            source=False,
        )
        return [r["text"] for r in response["suggest"]["complete"][0]["options"]]
