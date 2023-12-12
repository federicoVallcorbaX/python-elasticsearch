from functools import lru_cache
from enum import Enum

import openai
import requests


EMBEDDINGS_GENERATOR_URL = "http://embeddings-generator:3000/embedding"
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"


class EmbeddingType(str, Enum):
    OPENAI = "openai"
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"


@lru_cache()
def get_embedding_for_text(text: str, embedding_type: EmbeddingType) -> list[float]:
    if embedding_type in [EmbeddingType.SYMMETRIC, EmbeddingType.ASYMMETRIC]:
        sbert_response = requests.post(
            EMBEDDINGS_GENERATOR_URL, json={"text": text, "type": embedding_type}
        )
        return sbert_response.json()["embedding"]
    elif embedding_type == EmbeddingType.OPENAI:
        openai_response = openai.Embedding.create(
            input=text, model=OPENAI_EMBEDDING_MODEL
        )
        return openai_response["data"][0]["embedding"]
    else:
        raise NotImplementedError
