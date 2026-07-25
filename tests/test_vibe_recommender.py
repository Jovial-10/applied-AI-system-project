import numpy as np

from src.vibe_recommender import VibeRecommender, song_to_text

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


def test_song_to_text_includes_identifying_fields():
    text = song_to_text(SONGS[0])
    assert "Focus Flow" in text
    assert "LoRoom" in text
    assert "lofi" in text