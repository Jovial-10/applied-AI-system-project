"""
Command line runner for Symphony's vibe/RAG recommender.

Ranks songs by how closely their embedding matches a free-text "vibe" query.
The catalog is the text-only vibe catalog built from Spotify search (see
src/catalog_builder.py:build_vibe_catalog).

Run with: python -m src.main --vibe "rainy day coding music"
"""

import argparse

from .vibe_recommender import VibeRecommender, load_vibe_catalog

VIBE_CATALOG = "data/songs_vibe.csv"

# A few example queries to run when no --vibe is passed, so the CLI still
# demonstrates the recommender out of the box.
EXAMPLE_QUERIES = [
    "rainy day coding session",
    "hype gym workout pump",
    "late night heartbreak drive",
]


def print_vibe_recommendations(query: str, recommender: VibeRecommender) -> None:
    """Print the top 5 songs ranked by semantic similarity to a free-text query."""
    results = recommender.recommend(query, k=5)
    print(f'\n=== Vibe query: "{query}" ===\n')
    for rank, (song, score) in enumerate(results, start=1):
        print(f"{rank}. {song['title']} by {song['artist']} ({song['genre']}) - Similarity: {score:.2f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Symphony vibe recommender")
    parser.add_argument(
        "--vibe",
        metavar="WORDS",
        help='Free-text vibe query, e.g. --vibe "rainy day coding music"',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    songs = load_vibe_catalog(VIBE_CATALOG)
    recommender = VibeRecommender(songs)

    queries = [args.vibe] if args.vibe else EXAMPLE_QUERIES
    for query in queries:
        print_vibe_recommendations(query, recommender)


if __name__ == "__main__":
    main()
