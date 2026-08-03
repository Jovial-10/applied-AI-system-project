"""
Builds data/songs_vibe.csv: the text-only catalog (id/title/artist/genre/
image_url) that powers Symphony's vibe/RAG search, sourced from live Spotify
search.

Spotify tracks don't carry a `genre` field directly (the Get Artist endpoint's
`genres` field came back null for every artist we tried — a current,
undocumented Spotify API limitation, confirmed by inspecting the raw cached
responses). So instead each track's genre is the *bucket* its search seed
belongs to (see GENRE_SEED_GROUPS below) — several specific sub-genre seeds per
bucket so the catalog isn't limited to whatever Spotify's search ranks #1 for
one broad term. Spotify's `genre:"..."` search filter honors this reasonably
well but not perfectly, so a handful of results are a loose fit for their
bucket — see model_card.md for this tradeoff.

The vibe catalog is text-only, so it only needs the Search endpoint and can
scale to hundreds of tracks per build.

Run with: python -m src.catalog_builder
"""
import csv
from pathlib import Path
from typing import List

from .spotify_client import SpotifyClient

# Each bucket keeps a controlled genre label (so the catalog has a meaningful
# genre for display/explanations) but is sourced from several sub-genre search
# seeds, so one bucket isn't just Spotify's single top result for one broad
# term.
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
    "reggae": ["reggae", "dub", "roots reggae"],
    "blues": ["blues", "chicago blues", "delta blues"],
    "gospel": ["gospel", "christian gospel", "contemporary gospel"],
    "k-pop": ["k-pop", "korean pop", "k-pop girl group"],
    "afrobeats": ["afrobeats", "afropop", "afro fusion"],
    "disco": ["disco", "nu-disco", "disco funk"],
    "funk": ["funk", "p-funk", "funk rock"],
    "trance": ["trance", "progressive trance", "uplifting trance"],
    "drum and bass": ["drum and bass", "jungle", "liquid dnb"],
    "dubstep": ["dubstep", "riddim", "brostep"],
    "post-punk": ["post-punk", "gothic rock", "cold wave"],
    "shoegaze": ["shoegaze", "dream pop", "noise pop"],
    "grunge": ["grunge", "post-grunge", "90s alt rock"],
    "bluegrass": ["bluegrass", "newgrass", "old-time"],
    "flamenco": ["flamenco", "spanish guitar", "rumba flamenca"],
    "opera": ["opera", "operatic pop", "classical vocal"],
    "world": ["world music", "afrobeat world", "ethnic fusion"],
    "trip-hop": ["trip-hop", "downtempo trip hop", "chillstep"],
    "emo": ["emo", "emo pop", "midwest emo"],
    "bossa nova": ["bossa nova", "brazilian jazz", "samba jazz"],
}

# This app's search endpoint 400s on limit > 10 (an undocumented restriction —
# confirmed empirically, not in Spotify's docs, which advertise a max of 50).
# So VIBE_TRACKS_PER_QUERY stays at the real ceiling and we page with `offset`
# instead to go deeper per seed. 37 genre buckets x up to 40 songs each gives
# headroom well past 1000 songs; actual yield is lower since niche seeds (e.g.
# "flamenco") don't all have 40 distinct results to page through.
VIBE_TRACKS_PER_QUERY = 10
VIBE_MAX_PAGES_PER_SEED = 8
VIBE_MAX_SONGS_PER_GENRE = 40
VIBE_OUTPUT_PATH = Path("data/songs_vibe.csv")
VIBE_CSV_COLUMNS = ["id", "title", "artist", "genre", "image_url"]

# Spotify's search response lists each album's cover art largest-first
# (typically 640/300/64px). 300px is plenty for a card thumbnail and lighter
# to ship than the 640px original.
ALBUM_IMAGE_SIZE_PREFERENCE = [300, 640, 64]


def _album_image_url(track: dict) -> str:
    images = track.get("album", {}).get("images", [])
    if not images:
        return ""
    by_width = {img["width"]: img["url"] for img in images}
    for width in ALBUM_IMAGE_SIZE_PREFERENCE:
        if width in by_width:
            return by_width[width]
    return images[0]["url"]


def build_vibe_catalog() -> List[dict]:
    """Search-only catalog for the vibe/RAG query path — no audio-features call,
    so it can scale to hundreds of tracks per build."""
    client = SpotifyClient()
    rows = []
    seen_track_ids = set()

    for genre, seeds in GENRE_SEED_GROUPS.items():
        genre_count = 0
        for seed in seeds:
            if genre_count >= VIBE_MAX_SONGS_PER_GENRE:
                break
            for page in range(VIBE_MAX_PAGES_PER_SEED):
                if genre_count >= VIBE_MAX_SONGS_PER_GENRE:
                    break
                tracks = client.search_tracks(
                    f'genre:"{seed}"', limit=VIBE_TRACKS_PER_QUERY, offset=page * VIBE_TRACKS_PER_QUERY
                )
                if not tracks:
                    break  # this seed's results are exhausted; move to the next seed
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
                        "image_url": _album_image_url(track),
                    })
                    genre_count += 1
                if len(tracks) < VIBE_TRACKS_PER_QUERY:
                    break  # short page means no more results past this point

    return rows


def main() -> None:
    vibe_rows = build_vibe_catalog()
    VIBE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VIBE_OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=VIBE_CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(vibe_rows)
    print(f"Wrote {len(vibe_rows)} songs to {VIBE_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
