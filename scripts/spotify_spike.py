"""
One-off feasibility check: can this app read audio-features from Spotify?

Spotify restricted the Get Audio Features endpoint for new developer apps in
late 2024 — this script answers that question empirically instead of assuming
either way, so we know whether to source energy/valence/etc. live from
Spotify or keep them from our own dataset.

Usage:
    python -m scripts.spotify_spike
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")


def get_token() -> str:
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def search_track(token: str, query: str) -> dict:
    resp = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": query, "type": "track", "limit": 1},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["tracks"]["items"][0]


def try_audio_features(token: str, track_id: str) -> None:
    resp = requests.get(
        f"https://api.spotify.com/v1/audio-features/{track_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    print(f"GET /v1/audio-features/{track_id} -> {resp.status_code}")
    print(resp.json())


def main() -> None:
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in .env")
        sys.exit(1)

    token = get_token()
    print("Auth OK, got access token.\n")

    track = search_track(token, "track:Blinding Lights artist:The Weeknd")
    print(f"Found track: {track['name']} by {track['artists'][0]['name']} ({track['id']})\n")

    try_audio_features(token, track["id"])


if __name__ == "__main__":
    main()
