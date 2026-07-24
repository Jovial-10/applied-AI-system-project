"""
Builds data/songs_spotify.csv: a real-track replacement for the hand-authored
data/songs.csv, using live Spotify search + audio-features.

Spotify tracks don't carry a `genre` or `mood` field directly, so both are
derived rather than pulled verbatim:
- genre: the Get Artist endpoint's `genres` field came back null for every
  artist we tried (a current, undocumented Spotify API limitation — not a
  bug here, confirmed by inspecting the raw cached responses). So instead
  we use the `genre:"..."` search-filter term itself as the label. Spotify's
  search ranking honors that filter reasonably well but not perfectly, so
  a handful of results are a loose fit for their seed genre — see
  model_card.md for this tradeoff.
- mood: derived from the audio-feature quadrant (valence x energy), since
  Spotify has no mood label at all. This is a real modeling choice, not a
  Spotify fact — see model_card.md for the tradeoff.

Run with: python -m src.catalog_builder
"""
import csv
from pathlib import Path
from typing import List, Optional

from .spotify_client import SpotifyClient

# One search per genre bucket we want represented in the catalog. Some genres
# need an alternate query tried if the first turns up nothing.
GENRE_SEEDS = [
    "pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop",
    "edm", "country", "r&b", "metal", "folk", "soul", "hip-hop", "latin",
    "classical", "punk",
]
GENRE_QUERY_FALLBACKS = {"lofi": "lo-fi"}

OUTPUT_PATH = Path("data/songs_spotify.csv")
CSV_COLUMNS = [
    "id", "title", "artist", "genre", "mood",
    "energy", "tempo_bpm", "valence", "danceability", "acousticness",
]


def derive_mood(energy: float, valence: float) -> str:
    """Bucket mood from the valence/energy quadrant (Russell's circumplex model)."""
    if valence >= 0.5 and energy >= 0.5:
        return "energetic"
    if valence >= 0.5 and energy < 0.5:
        return "chill"
    if valence < 0.5 and energy >= 0.5:
        return "intense"
    return "melancholy"


def fetch_song(client: SpotifyClient, seed_genre: str, song_id: int) -> Optional[dict]:
    track = client.search_track(f'genre:"{seed_genre}"')
    if track is None and seed_genre in GENRE_QUERY_FALLBACKS:
        track = client.search_track(f'genre:"{GENRE_QUERY_FALLBACKS[seed_genre]}"')
    if track is None:
        return None

    features = client.get_audio_features(track["id"])

    return {
        "id": song_id,
        "title": track["name"],
        "artist": track["artists"][0]["name"],
        "genre": seed_genre,
        "mood": derive_mood(features["energy"], features["valence"]),
        "energy": features["energy"],
        "tempo_bpm": features["tempo"],
        "valence": features["valence"],
        "danceability": features["danceability"],
        "acousticness": features["acousticness"],
    }


def build_catalog() -> List[dict]:
    client = SpotifyClient()
    rows = []
    for i, seed_genre in enumerate(GENRE_SEEDS, start=1):
        row = fetch_song(client, seed_genre, i)
        if row is not None:
            rows.append(row)
    return rows


def main() -> None:
    rows = build_catalog()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} songs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
