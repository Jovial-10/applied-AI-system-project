import numpy as np

from src.vibe_recommender import EMBEDDING_MODEL_NAME, VibeRecommender, song_to_text

SONGS = [
    {"id": 1, "title": "Focus Flow", "artist": "LoRoom", "genre": "lofi", "mood": "chill"},
    {"id": 2, "title": "Riot Static", "artist": "The Broken Amps", "genre": "punk", "mood": "rebellious"},
]

# Deterministic fake embeddings keyed by exact blurb/query text, so the test
# never downloads a model or hits the network.
FAKE_VECTORS = {
    song_to_text(SONGS[0]): [1.0, 0.0],
    song_to_text(SONGS[1]): [0.0, 1.0],
    "chill lofi vibes": [0.9, 0.1],
}


def fake_embed_fn(texts):
    return np.array([FAKE_VECTORS[text] for text in texts])


def test_recommend_ranks_closest_song_first():
    recommender = VibeRecommender(SONGS, embed_fn=fake_embed_fn)
    results = recommender.recommend("chill lofi vibes", k=2)

    assert [song["title"] for song, _score in results] == ["Focus Flow", "Riot Static"]
    assert results[0][1] > results[1][1]


def test_song_to_text_excludes_title_to_avoid_literal_overlap():
    """The blurb deliberately omits the title and artist so a literal word in
    a title can't dominate the match (e.g. "Rain" for "rainy day coding").
    A no-vibe song falls back to a genre descriptor — still title-free."""
    text = song_to_text(SONGS[0])
    assert "Focus Flow" not in text
    assert "LoRoom" not in text
    assert "lofi" in text  # genre descriptor still carries the semantic signal


def test_song_to_text_is_the_vibe_line_alone_when_present():
    """When a song has a vibe line, the blurb IS that line verbatim — no
    title, artist, or genre descriptor wrapped around it."""
    song = {"id": 7, "title": "Rainy Days", "artist": "Someone", "genre": "pop",
            "vibe": "hazy, tape-warm calm for a slow afternoon"}
    assert song_to_text(song) == "hazy, tape-warm calm for a slow afternoon"


def test_song_to_text_prefers_vibe_line_over_genre_descriptor():
    """When a song carries a hand-written vibe line, the blurb is built from
    it (a per-song semantic signal) rather than the generic per-genre
    descriptor that made every song of a genre embed to near-identical text."""
    song = {"id": 9, "title": "Velvet Hour", "artist": "Nocturne", "genre": "pop",
            "vibe": "silky, bittersweet regret — guilt wrapped in velvet"}
    text = song_to_text(song)
    assert "silky, bittersweet regret" in text
    # The genre-descriptor fallback should not fire when a vibe is present.
    assert "radio-ready energy" not in text


def test_recommend_downweights_inferred_on_a_close_match():
    """On a near-tie, a verified ("known") song ranks ahead of an inferred one
    whose raw similarity is marginally higher, because inferred rows are
    down-weighted. See INFERRED_WEIGHT in src/vibe_recommender.py."""
    songs = [
        {"id": 1, "title": "Known Song", "artist": "A", "genre": "pop", "confidence": "known"},
        {"id": 2, "title": "Inferred Song", "artist": "B", "genre": "pop", "confidence": "inferred"},
    ]
    vectors = {
        song_to_text(songs[0]): [1.0, 0.0],
        song_to_text(songs[1]): [0.96, 0.28],  # raw cosine ~0.96 vs known's 0.94...
        "a warm pop vibe": [0.94, 0.34],
    }
    embed_fn = lambda texts: np.array([vectors[t] for t in texts])
    results = VibeRecommender(songs, embed_fn=embed_fn).recommend("a warm pop vibe", k=2)
    # Inferred's raw similarity is higher, but 0.9x weighting flips the order.
    assert results[0][0]["title"] == "Known Song"


def test_recommend_resists_literal_title_overlap_over_genre_mismatch():
    """Regression guard for a real production bug: a song whose title happens
    to share a literal word with the query (e.g. "High Hopes" for a "high
    energy workout" search) could out-rank a song whose *genre* is the
    actually-correct vibe, purely on that coincidental overlap. Uses the real
    embedding model (no fake vectors) since the bug is about real model
    behavior on short text, not the ranking logic around it.

    NOTE: enriching the blurb with a genre-vibe descriptor (see song_to_text)
    fixes this for most literal-overlap cases, including this one — but it's
    a mitigation, not a guarantee. Verified against the real model that an
    exact, emotionally loaded word shared between query and title (e.g.
    "party", "dark") can still occasionally win even after this fix; that
    residual failure mode isn't covered here. A stricter fix (blending a
    title-only similarity with a genre-vibe-only similarity, rather than one
    combined embedding) would close that gap but wasn't the approach chosen.
    """
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    embed_fn = lambda texts: model.encode(texts, normalize_embeddings=True)

    songs = [
        # Wrong genre for the query, but the title literally contains "High".
        {"id": 1, "title": "High Hopes", "artist": "Some Artist", "genre": "ambient"},
        # The actually energetic genre, with no literal word overlap at all.
        {"id": 2, "title": "Thunderstruck", "artist": "AC/DC", "genre": "rock"},
    ]
    recommender = VibeRecommender(songs, embed_fn=embed_fn)
    results = recommender.recommend("high energy workout", k=2)

    assert results[0][0]["title"] == "Thunderstruck"