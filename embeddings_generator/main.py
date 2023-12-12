from typing import Any

from fastapi import FastAPI

from schemas import EmbeddingsRequest, EmbeddingsResponse
from embedding_generator import get_embedding_sbert


app = FastAPI()


@app.post("/embedding", response_model=EmbeddingsResponse)
def get_embbeding_for_text(body: EmbeddingsRequest) -> Any:
    embedding = get_embedding_sbert(body.text, body.type)
    return {"embedding": embedding}
