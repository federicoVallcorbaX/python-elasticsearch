import os
import argparse
import pandas as pd

from embedding_generator import EmbeddingTypes, get_embedding_sbert


def _main(data_folder: str, verbose: bool = False) -> None:
    # pd.options.mode.chained_assignment = None

    batches = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]
    for batch in batches:
        offset = batch[0] * 1000
        limit = batch[1] * 1000 if batch[1] else None
        df = pd.read_parquet(os.path.join(data_folder, "movie_features.parquet"))
        df = df[offset:limit]
        openai_df = pd.read_parquet(os.path.join(data_folder, "openai_embeddings.parquet"))
        openai_df = openai_df[offset:limit]
        symetric_embeddings = []
        asymetric_embeddings = []
        count = 0
        total = len(df)
        print(f"Uploading batch {offset}:{limit}")
        for i, row in df.iterrows():
            count += 1
            text = f"Movie: {row.get('title')}. Overview: {row.get('overview')}"
            symetric_embeddings.append(get_embedding_sbert(text, EmbeddingTypes.SYMMETRIC))
            asymetric_embeddings.append(get_embedding_sbert(text, EmbeddingTypes.ASYMMETRIC))
            if verbose and count % 500 == 0:
                print(f"Generated {count}/{total} embeddings")
        df["sbert_symmetric_embedding"] = symetric_embeddings
        df["sbert_asymmetric_embedding"] = asymetric_embeddings
        df["openai_embedding"] = openai_df["embedding"]
        df.to_parquet(os.path.join(data_folder, f"movies_with_embeddings_{offset}-{limit}.parquet"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates SBERT embeddings for the movies")
    parser.add_argument("--data_folder", "-f", type=str, default="../data/")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()
    data_folder = args.data_folder
    verbose = args.verbose

    _main(data_folder, verbose)
