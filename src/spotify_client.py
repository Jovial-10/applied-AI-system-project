"""
Thin wrapper around the Spotify Web API (Client Credentials flow).

Only uses endpoints available on the standard free developer tier: token
exchange, search, and audio-features. Responses are cached to a local JSON
file so repeated builds and tests don't need a live network call or a
Spotify app registered at all once the cache is warm.
"""
import json
import os
import time
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"
DEFAULT_CACHE_PATH = Path("data/spotify_cache.json")


class SpotifyClient:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        cache_path: Path = DEFAULT_CACHE_PATH,
    ):
        self.client_id = client_id or os.environ.get("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET")
        self.cache_path = cache_path
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        if self.cache_path.exists():
            with open(self.cache_path) as f:
                return json.load(f)
        return {}

    def _save_cache(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump(self._cache, f, indent=2)

    def _get_token(self) -> str:
        if self._token and time.time() < self._token_expires_at:
            return self._token

        if not self.client_id or not self.client_secret:
            raise RuntimeError(
                "SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET not set (check .env)"
            )

        resp = requests.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(self.client_id, self.client_secret),
            timeout=10,
        )
        resp.raise_for_status()
        payload = resp.json()
        self._token = payload["access_token"]
        self._token_expires_at = time.time() + payload["expires_in"] - 30
        return self._token

    def _cached_get(self, cache_key: str, url: str, params: Optional[dict] = None) -> dict:
        if cache_key in self._cache:
            return self._cache[cache_key]

        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {self._get_token()}"},
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self._cache[cache_key] = data
        self._save_cache()
        return data

    def search_track(self, query: str) -> Optional[dict]:
        """Return the top track result for a free-text search query, or None."""
        cache_key = f"search:{query}"
        data = self._cached_get(cache_key, f"{API_BASE}/search", {"q": query, "type": "track", "limit": 1})
        items = data.get("tracks", {}).get("items", [])
        return items[0] if items else None

    def get_audio_features(self, track_id: str) -> dict:
        return self._cached_get(f"audio_features:{track_id}", f"{API_BASE}/audio-features/{track_id}")

    def get_artist(self, artist_id: str) -> dict:
        return self._cached_get(f"artist:{artist_id}", f"{API_BASE}/artists/{artist_id}")
