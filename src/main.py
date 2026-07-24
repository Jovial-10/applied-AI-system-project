"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import os

from .recommender import load_songs, recommend_songs

# Prefer the live Spotify-backed catalog when it's been built (see
# src/catalog_builder.py); fall back to the static CSV so this still runs
# for anyone without Spotify credentials.
SPOTIFY_CATALOG = "data/songs_spotify.csv"
STATIC_CATALOG = "data/songs.csv"

# Starter example profile
STARTER_PROFILE = ("pop/happy", {"genre": "pop", "mood": "happy", "energy": 0.8})

# Edge case profiles designed to stress-test the Algorithm Recipe: each pairs
# a favorite genre with attributes that genre's real songs in the catalog
# don't actually have, so the genre-match bonus and the closeness terms end
# up pulling the score in opposite directions.
EDGE_CASE_PROFILES = [
    ("Slow acoustic rock", {"genre": "rock", "mood": "relaxed", "energy": 0.25, "likes_acoustic": True}),
    ("Low-energy pop", {"genre": "pop", "mood": "chill", "energy": 0.15, "likes_acoustic": True}),
    ("Deep intense country", {"genre": "country", "mood": "intense", "energy": 0.85, "likes_acoustic": True}),
]


def print_recommendations(label: str, user_prefs: dict, songs: list) -> None:
    """Print the top 5 ranked recommendations for one user profile."""
    recommendations = recommend_songs(user_prefs, songs, k=5)
    profile_summary = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print(f"\n=== {label} ({profile_summary}) ===\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - Score: {score:.2f}")
        print(f"   Reasons: {explanation}")
        print()


def main() -> None:
    catalog_path = SPOTIFY_CATALOG if os.path.exists(SPOTIFY_CATALOG) else STATIC_CATALOG
    songs = load_songs(catalog_path)

    print_recommendations(*STARTER_PROFILE, songs)
    for label, user_prefs in EDGE_CASE_PROFILES:
        print_recommendations(label, user_prefs, songs)


if __name__ == "__main__":
    main()
