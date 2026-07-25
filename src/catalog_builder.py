"""
Builds data/songs_spotify.csv: a real-track replacement for the hand-authored
data/songs.csv, using live Spotify search + audio-features.

Spotify tracks don't carry a `genre` or `mood` field directly, so both are
derived rather than pulled verbatim:
- genre: the Get Artist endpoint's `genres` field came back null for every
  artist we tried (a current, undocumented Spotify API limitation — not a
  bug here, confirmed by inspecting the raw cached responses). So instead
  each track's genre is the *bucket* its search seed belongs to (see
  GENRE_SEED_GROUPS below) — several specific sub-genre seeds per bucket so
  the catalog isn't limited to whatever Spotify's search ranks #1 for one
  broad term. Spotify's `genre:"..."` search filter honors this reasonably
  well but not perfectly, so a handful of results are a loose fit for their
  bucket — see model_card.md for this tradeoff.
- mood: derived from the audio-feature quadrant (valence x energy), since
  Spotify has no mood label at all. This is a real modeling choice, not a
  Spotify fact — see model_card.md for the tradeoff.

Audio-features access is capped at roughly the first ~17 tracks this app
ever requested — every track fetched since then 403s, with no Retry-After
(not an ordinary rate limit; see model_card.md). So build_catalog() stays
deliberately small (one track per genre bucket, cached) rather than
retrying a wall that isn't coming down. The vibe/RAG catalog doesn't have
this problem — it only needs Search, which is unaffected — so it scales
independently via build_vibe_catalog().

Run with: python -m src.catalog_builder
"""
import csv
from pathlib import Path
from typing import List

import requests

from .spotify_client import SpotifyClient

# Each bucket keeps the original controlled vocabulary (so exact-match genre
# scoring still has something meaningful to match against) but is sourced
# from several sub-genre search seeds, so one bucket isn't just Spotify's
# single top result for one broad term.
GENRE_SEED_GROUPS = {
    "pop": ["pop", "dance pop", "electropop", "pop rock"],
    "lofi": ["lofi", "lo-fi", "chillhop"],
    "rock": ["rock", "alternative rock", "classic rock", "arena rock"],
    "ambient": ["ambient", "ambient pop", "downtempo"],
    "jazz": ["jazz", "smooth jazz", "vocal jazz"],
    "synthwave": ["synthwave", "retrowave", "electro"],
    "indie pop": ["indie pop", "indie rock", "bedroom pop"],
    "edm": ["edm", "house", "electro house"],
    "country": ["country", "country pop", "outlaw country"],
    "r&b": ["r&b", "neo soul", "contemporary r&b"],
    "metal": ["metal", "nu metal", "metalcore"],
    "folk": ["folk", "indie folk", "folk pop"],
    "soul": ["soul", "motown", "funk soul"],
    "hip-hop": ["hip-hop", "rap", "trap"],
    "latin": ["latin", "reggaeton", "latin pop"],
    "classical": ["classical", "orchestral", "piano"],
    "punk": ["punk", "pop punk", "punk rock"],
}

OUTPUT_PATH = Path("data/songs_spotify.csv")
CSV_COLUMNS = [
    "id", "title", "artist", "genre", "mood",
    "energy", "tempo_bpm", "valence", "danceability", "acousticness",
]

# The vibe (RAG) catalog is text-only — title/artist/genre — so it only needs
# Search, which isn't rate-blocked the way audio-features turned out to be.
# It can scale independently of the small audio-features catalog above.
VIBE_TRACKS_PER_QUERY = 5
VIBE_MAX_SONGS_PER_GENRE = 8
VIBE_OUTPUT_PATH = Path("data/songs_vibe.csv")
VIBE_CSV_COLUMNS = ["id", "title", "artist", "genre"]


def derive_mood(energy: float, valence: float) -> str:
    """Bucket mood from the valence/energy quadrant (Russell's circumplex model)."""
    if valence >= 0.5 and energy >= 0.5:
        return "energetic"
    if valence >= 0.5 and energy < 0.5:
        return "chill"
    if valence < 0.5 and energy >= 0.5:
        return "intense"
    return "melancholy"


def build_row(client: SpotifyClient, track: dict, genre: str, song_id: int) -> dict:
    features = client.get_audio_features(track["id"])
    return {
        "id": song_id,
        "title": track["name"],
        "artist": track["artists"][0]["name"],
        "genre": genre,
        "mood": derive_mood(features["energy"], features["valence"]),
        "energy": features["energy"],
        "tempo_bpm": features["tempo"],
        "valence": features["valence"],
        "danceability": features["danceability"],
        "acousticness": features["acousticness"],
    }


def build_catalog() -> List[dict]:
    """One real, audio-feature-backed track per genre bucket. Tries each
    bucket's seeds in order and stops at the first one that both returns a
    search result and clears the audio-features call, rather than burning
    calls chasing tracks the block will reject anyway."""
    client = SpotifyClient()
    rows = []
    seen_track_ids = set()

    for genre, seeds in GENRE_SEED_GROUPS.items():
        for seed in seeds:
            track = client.search_track(f'genre:"{seed}"')
            if track is None or track["id"] in seen_track_ids:
                continue
            try:
                row = build_row(client, track, genre, song_id=len(rows) + 1)
            except requests.exceptions.HTTPError:
                # This track's audio-features call hit the block (or, rarely,
                # some other per-track restriction). Try this bucket's next
                # seed instead of giving up on the whole genre.
                continue
            seen_track_ids.add(track["id"])
            rows.append(row)
            break

    return rows


def build_vibe_catalog() -> List[dict]:
    """Search-only catalog for the vibe/RAG query path — no audio-features call,
    so it isn't subject to that endpoint's block and can scale further."""
    client = SpotifyClient()
    rows = []
    seen_track_ids = set()

    for genre, seeds in GENRE_SEED_GROUPS.items():
        genre_count = 0
        for seed in seeds:
            if genre_count >= VIBE_MAX_SONGS_PER_GENRE:
                break
            tracks = client.search_tracks(f'genre:"{seed}"', limit=VIBE_TRACKS_PER_QUERY)
            for track in tracks:
                if genre_count >= VIBE_MAX_SONGS_PER_GENRE:
                    break
                if track["id"] in seen_track_ids:
                    continue
                seen_track_ids.add(track["id"])
                rows.append({
                    "id": len(rows) + 1,
                    "title": track["name"],
                    "artist": track["artists"][0]["name"],
                    "genre": genre,
                })
                genre_count += 1

    return rows


def main() -> None:
    rows = build_catalog()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} songs to {OUTPUT_PATH}")

    vibe_rows = build_vibe_catalog()
    VIBE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VIBE_OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=VIBE_CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(vibe_rows)
    print(f"Wrote {len(vibe_rows)} songs to {VIBE_OUTPUT_PATH}")


if __name__ == "__main__":
    main()