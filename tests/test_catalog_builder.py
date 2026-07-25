from src.catalog_builder import derive_mood
from src.spotify_client import SpotifyClient


def test_derive_mood_quadrants():
    assert derive_mood(energy=0.8, valence=0.8) == "energetic"
    assert derive_mood(energy=0.2, valence=0.8) == "chill"
    assert derive_mood(energy=0.8, valence=0.2) == "intense"
    assert derive_mood(energy=0.2, valence=0.2) == "melancholy"


def test_spotify_client_reads_from_cache_without_network(tmp_path):
    cache_path = tmp_path / "cache.json"
    cache_path.write_text(
        '{"search:genre:\\"pop\\":limit1": {"tracks": {"items": [{"id": "abc123"}]}}}'
    )

    client = SpotifyClient(client_id="unused", client_secret="unused", cache_path=cache_path)
    track = client.search_track('genre:"pop"')

    assert track == {"id": "abc123"}
