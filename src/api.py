"""
Ravensburger tiptoi API client.
Reverse engineered from tiptoi® Manager v5.2.
"""

import os
import json
import time
import requests
from typing import Optional, Dict, Any, List, Callable

CACHE_DIR = os.path.expanduser("~/.cache/tiptoi-manager")
IMAGE_CACHE_DIR = os.path.join(CACHE_DIR, "images")

class TiptoiAPI:
    OAUTH_URL = "https://oauth.ravensburger.com/oauth/token"
    BASE_URL = "https://ttapiv2.ravensburger.com/api/v2"
    
    CLIENT_ID = "tiptoi-manager-v2"
    CLIENT_SECRET = "CYmWkYyhY3traWuGd5cHcNV"

    def __init__(self, locale: str = "de-DE"):
        self.locale = locale
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0
        os.makedirs(CACHE_DIR, exist_ok=True)
        os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

    def get_token(self, force_refresh: bool = False) -> str:
        """Obtains or reuses an OAuth Bearer token using client_credentials grant."""
        if not force_refresh and self._access_token and time.time() < (self._token_expiry - 60):
            return self._access_token

        # Check cached token on disk
        token_file = os.path.join(CACHE_DIR, "token.json")
        if not force_refresh and os.path.exists(token_file):
            try:
                with open(token_file, "r") as f:
                    data = json.load(f)
                    if time.time() < (data.get("expiry", 0) - 60):
                        self._access_token = data.get("access_token")
                        self._token_expiry = data.get("expiry", 0)
                        if self._access_token:
                            return self._access_token
            except Exception:
                pass

        resp = requests.post(
            self.OAUTH_URL,
            auth=(self.CLIENT_ID, self.CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        self._token_expiry = time.time() + expires_in

        try:
            with open(token_file, "w") as f:
                json.dump({"access_token": self._access_token, "expiry": self._token_expiry}, f)
        except Exception:
            pass

        return self._access_token

    def _get_auth_headers(self) -> Dict[str, str]:
        token = self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "tiptoi-manager/5.2 (Linux; Linux x86_64)",
        }

    def get_catalog(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetches the full product and audio catalog for the specified locale."""
        cache_file = os.path.join(CACHE_DIR, f"catalog_{self.locale}.json")
        if not force_refresh and os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                    # Cache valid for 24h
                    if time.time() - os.path.getmtime(cache_file) < 86400:
                        return cached
            except Exception:
                pass

        url = f"{self.BASE_URL}/catalog/{self.locale}"
        try:
            resp = requests.get(url, headers=self._get_auth_headers(), timeout=20)
            if resp.status_code == 401:
                # Token expired, retry once
                resp = requests.get(url, headers={"Authorization": f"Bearer {self.get_token(force_refresh=True)}"}, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
        except Exception as e:
            # Fall back to stale cache if offline
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            raise e

    def get_config(self, os_target: str = "WIN") -> Dict[str, Any]:
        """Fetches system configuration and latest firmware list."""
        url = f"{self.BASE_URL}/config/{self.locale}/{os_target}"
        resp = requests.get(url, headers=self._get_auth_headers(), timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_cached_image_path(self, url: str) -> str:
        """Returns local path for cached image; downloads if missing."""
        if not url:
            return ""
        filename = url.split("/")[-1].split("?")[0]
        # Avoid collisions by prefixing dimension if present
        parts = url.split("/")
        dim = parts[-2] if len(parts) >= 2 and parts[-2].isdigit() else "img"
        local_filename = f"{dim}_{filename}"
        local_path = os.path.join(IMAGE_CACHE_DIR, local_filename)

        if not os.path.exists(local_path):
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(r.content)
            except Exception as e:
                print(f"Failed to download image {url}: {e}")
                return ""
        return local_path

    def download_file(
        self,
        url: str,
        dest_path: str,
        on_progress: Optional[Callable[[int, int], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> bool:
        """
        Downloads a file (e.g. .gme or .upd) to destination path with progress report.
        Supports resume or atomic temp file write.
        """
        temp_dest = dest_path + ".download"
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            downloaded = 0

            with open(temp_dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=128 * 1024):
                    if cancel_check and cancel_check():
                        f.close()
                        if os.path.exists(temp_dest):
                            os.remove(temp_dest)
                        return False
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if on_progress:
                            on_progress(downloaded, total_size)

            os.replace(temp_dest, dest_path)
            # Sync filesystem so USB safely retains the file
            try:
                os.sync()
            except Exception:
                pass
            return True
        except Exception as e:
            if os.path.exists(temp_dest):
                try:
                    os.remove(temp_dest)
                except Exception:
                    pass
            raise e
