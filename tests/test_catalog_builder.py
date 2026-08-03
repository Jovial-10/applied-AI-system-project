from src.spotify_client import SpotifyClient


def test_spotify_client_reads_from_cache_without_network(tmp_path):
    cache_path = tmp_path / "cache.json"
    cache_path.write_text(
        '{"search:genre:\\"pop\\":limit1:offset0": {"tracks": {"items": [{"id": "abc123"}]}}}'
    )

    client = SpotifyClient(client_id="unused", client_secret="unused", cache_path=cache_path)
    track = client.search_track('genre:"pop"')

    assert track == {"id": "abc123"}
