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

# Similarity multiplier for songs whose vibe line is inferred rather than
# verified. Mirrored in web/src/lib/similarity.js — keep both in sync.
INFERRED_WEIGHT = 0.9

EmbedFn = Callable[[List[str]], np.ndarray]

# A bare genre noun ("lofi") gives the embedding model almost nothing to work
# with, so a literal word shared between a title and the query (e.g. a lofi
# song called "Bass Party" matching a "hype party energy" search) can
# dominate similarity even when the genre itself is the wrong vibe entirely.
# Describing each genre's actual vibe gives the model real semantic signal to
# weigh against that kind of coincidental title overlap. Mirrored in
# web/src/lib/explain.js (also used there for the UI's "why this matches"
# text) — keep both in sync if you touch one.
GENRE_VIBE = {
    "pop": ("polished hooks and an upbeat, radio-ready energy", "feel-good"),
    "lofi": ("warm tape hiss and a slow, laid-back beat", "chill"),
    "rock": ("driving guitars and raw, live-band energy", "high-energy"),
    "ambient": ("airy pads and almost no percussion", "atmospheric"),
    "jazz": ("improvisational phrasing and a loose, swinging groove", "smooth"),
    "synthwave": ("retro synth arpeggios and a steady electronic pulse", "neon-lit, nostalgic"),
    "indie pop": ("breezy melodies and lo-fi production charm", "dreamy"),
    "edm": ("a pounding four-on-the-floor beat and big drops", "euphoric"),
    "country": ("twangy guitars and storytelling vocals", "nostalgic"),
    "r&b": ("smooth vocal runs and a laid-back groove", "sultry"),
    "metal": ("distorted riffs and aggressive percussion", "intense"),
    "folk": ("acoustic instrumentation and plainspoken lyrics", "earthy"),
    "soul": ("expressive vocals over a warm, groove-driven backbone", "soulful"),
    "hip-hop": ("a heavy beat and rhythmic vocal delivery", "confident"),
    "latin": ("percussive rhythms and danceable grooves", "vibrant"),
    "classical": ("orchestral arrangement and no vocals", "reflective"),
    "punk": ("fast tempos and raw, stripped-down energy", "rebellious"),
    "reggae": ("off-beat guitar skanks and a relaxed groove", "laid-back"),
    "blues": ("expressive guitar bends and a slow, soulful groove", "moody"),
    "gospel": ("layered vocal harmonies and an uplifting build", "uplifting"),
    "k-pop": ("polished production and high-energy hooks", "energetic"),
    "afrobeats": ("syncopated percussion and a danceable groove", "vibrant"),
    "disco": ("a steady four-on-the-floor groove and lush strings", "danceable"),
    "funk": ("a syncopated bassline and a tight rhythmic groove", "groovy"),
    "trance": ("sweeping synth builds and a hypnotic tempo", "euphoric"),
    "drum and bass": ("fast breakbeats and deep basslines", "high-energy"),
    "dubstep": ("heavy sub-bass drops and syncopated rhythm", "intense"),
    "post-punk": ("angular guitars and a cool, detached tone", "moody"),
    "shoegaze": ("wall-of-sound guitar textures and hazy vocals", "dreamy"),
    "grunge": ("distorted guitars and a raw, unpolished edge", "brooding"),
    "bluegrass": ("fast picking and acoustic string arrangements", "lively"),
    "flamenco": ("intricate guitar work and passionate rhythm", "fiery"),
    "opera": ("a powerful vocal performance over orchestral backing", "dramatic"),
    "world": ("traditional instrumentation from outside the mainstream", "eclectic"),
    "trip-hop": ("a slow, downtempo beat and a hazy atmosphere", "moody"),
    "emo": ("raw, confessional vocals and emotional guitar hooks", "emotional"),
    "bossa nova": ("gentle nylon-string guitar and a soft samba sway", "relaxed"),
}


def song_to_text(song: dict) -> str:
    """Build the descriptive blurb a song is embedded from.

    Embeds each song from its hand-written `vibe` line ALONE (the `vibe`
    column in data/songs_vibe.csv), deliberately excluding the title and
    artist. Including the title meant a literal word in it (e.g. "Rain" in a
    title, for a "rainy day coding" query) could dominate the match even when
    the song's actual vibe was unrelated. The vibe line is the real semantic
    signal, so we match on it alone.

    Falls back to a genre descriptor only for a row with no vibe — also
    title-free, for the same reason. `mood` (present only on the small
    audio-feature catalog, absent on the search-only vibe catalog) enriches
    that fallback when available.
    """
    vibe_line = (song.get("vibe") or "").strip()
    if vibe_line:
        return vibe_line
    mood_part = f"{song['mood']} " if song.get("mood") else ""
    descriptor = GENRE_VIBE.get(song["genre"])
    if descriptor:
        feature, vibe = descriptor
        return f"A {mood_part}{song['genre']} song with {feature}, a {vibe} vibe."
    return f"A {mood_part}{song['genre']} song."


def load_vibe_catalog(csv_path: str) -> List[dict]:
    """Read the text-only vibe catalog (id/title/artist/genre, no audio features)."""
    with open(csv_path, newline="") as f:
        return [
            {
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "vibe": (row.get("vibe") or "").strip(),
                "confidence": (row.get("confidence") or "").strip(),
            }
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

        # Songs whose vibe line was inferred rather than verified (see the
        # `confidence` column in data/songs_vibe.csv) get their similarity
        # nudged down, so a verified song wins a close match. Small enough not
        # to bury a clearly-better inferred song.
        weights = np.array(
            [INFERRED_WEIGHT if song.get("confidence") == "inferred" else 1.0 for song in self.songs]
        )
        similarities = similarities * weights

        ranked = sorted(zip(self.songs, similarities), key=lambda pair: -pair[1])
        return [(song, float(score)) for song, score in ranked[:k]]