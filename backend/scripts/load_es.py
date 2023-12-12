from typing import Any, Generator

import pandas as pd

from services.search import ESManager


def _get_movies(file_path: str) -> Generator[dict, Any, Any]:
    df = pd.read_parquet(file_path)
    df.drop(
        columns=[
            "vote_count",
            "release_date",
            "created_at",
            "timestamp",
            "original_language",
            "collection",
            "producers",
            "production_countries",
            "tagline",
            "adult",
            "avg_cast_popularity",
            "avg_crew_popularity",
        ],
        inplace=True,
    )
    df.rename(columns={"protagonist": "protagonists"}, inplace=True)
    df["protagonists"] = df["protagonists"].apply(lambda x: x.tolist())
    df["genres"] = df["genres"].apply(lambda x: x.tolist())
    df["openai_embedding"] = df["openai_embedding"].apply(lambda x: x.tolist())
    df["sbert_symmetric_embedding"] = df["sbert_symmetric_embedding"].apply(
        lambda x: x.tolist()
    )
    df["sbert_asymmetric_embedding"] = df["sbert_asymmetric_embedding"].apply(
        lambda x: x.tolist()
    )
    for _, row in df.iterrows():
        movie_dict = row.to_dict()
        movie_dict['title_completion'] = {'input': movie_dict['title'], 'weight': int(movie_dict['popularity'])}
        yield movie_dict


def _main(file_paths: list[str]) -> None:
    em = ESManager()
    em.create_index(drop_index_if_exists=True)
    count = 0
    for file_path in file_paths:
        for movie in _get_movies(f"/data/{file_path}"):
            em.save_document(movie)
            count += 1
            if count % 500 == 0:
                print(f"Uploaded {count} movies into ES")


if __name__ == "__main__":
    batches = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]
    batch_size = 1000
    file_paths = [
        f"movies_with_embeddings_{b[0]*batch_size}-{b[1]*batch_size if b[1] else None}.parquet"
        for b in batches
    ]
    _main(file_paths)
