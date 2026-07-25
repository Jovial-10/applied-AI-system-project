"""
Free-text "vibe query" recommender: the user types a few descriptive words
("rainy day coding", "hype gym pump") and gets songs ranked by how closely
their embedding matches each song's embedding — a small RAG-style retrieval
step layered on top of the existing catalog, independent of the structured
UserProfile/Algorithm Recipe path in recommender.py.

No vector database: at catalog scale (tens to low hundreds of songs) this is
just a cosine similarity over an in-memory numpy matrix. Embeddings are local
(sentence-transformers), so this costs nothing to run.
"""
import csv
from typing import Callable, List, Tuple

import numpy as np

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

EmbedFn = Callable[[List[str]], np.ndarray]


def song_to_text(song: dict) -> str:
    """Build the descriptive blurb a song is embedded from.

    `mood` is optional: the small audio-feature catalog has it (derived from
    energy/valence), but the larger search-only vibe catalog doesn't, since
    deriving mood needs the audio-features call that's largely blocked.
    """
    mood_part = f" a {song['mood']}" if song.get("mood") else " a"
    return f"{song['title']} by {song['artist']}:{mood_part} {song['genre']} song"


def load_vibe_catalog(csv_path: str) -> List[dict]:
    """Read the text-only vibe catalog (id/title/artist/genre, no audio features)."""
    with open(csv_path, newline="") as f:
        return [
            {"id": int(row["id"]), "title": row["title"], "artist": row["artist"], "genre": row["genre"]}
            for row in csv.DictReader(f)
        ]


def _default_embed_fn() -> EmbedFn:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return lambda texts: model.encode(texts, normalize_embeddings=True)


class VibeRecommender:
    """Ranks songs by semantic similarity to a free-text query."""

    def __init__(self, songs: List[dict], embed_fn: EmbedFn = None):
        self.songs = songs
        self._embed_fn = embed_fn or _default_embed_fn()
        texts = [song_to_text(song) for song in songs]
        self._song_embeddings = np.asarray(self._embed_fn(texts))

    def recommend(self, query: str, k: int = 5) -> List[Tuple[dict, float]]:
        """Return the top k songs as (song, similarity) pairs, most similar first."""
        query_embedding = np.asarray(self._embed_fn([query]))[0]
        query_norm = np.linalg.norm(query_embedding)
        song_norms = np.linalg.norm(self._song_embeddings, axis=1)

        similarities = self._song_embeddings @ query_embedding
        with np.errstate(invalid="ignore", divide="ignore"):
            similarities = similarities / (song_norms * query_norm)
        similarities = np.nan_to_num(similarities)

        ranked = sorted(zip(self.songs, similarities), key=lambda pair: -pair[1])
        return [(song, float(score)) for song, score in ranked[:k]]