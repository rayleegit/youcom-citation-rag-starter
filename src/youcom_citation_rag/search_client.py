from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


SEARCH_ENDPOINT = "https://ydc-index.io/v1/search"


class YouSearchError(RuntimeError):
    """Raised when the You.com Search API cannot return usable results."""


@dataclass(frozen=True)
class YouSearchClient:
    api_key: str | None = None
    endpoint: str = SEARCH_ENDPOINT
    timeout_seconds: float = 20.0

    @classmethod
    def from_env(cls) -> "YouSearchClient":
        return cls(api_key=os.environ.get("YDC_API_KEY"))

    def search(self, query: str, count: int = 5) -> list[dict[str, Any]]:
        if not self.api_key:
            raise YouSearchError("Set YDC_API_KEY or run with --fixture for offline demos.")

        params = urllib.parse.urlencode({"query": query, "count": count})
        request = urllib.request.Request(
            f"{self.endpoint}?{params}",
            headers={"X-API-Key": self.api_key, "Accept": "application/json"},
            method="GET",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise YouSearchError(f"You.com Search API returned {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise YouSearchError(f"Could not reach You.com Search API: {exc.reason}") from exc

        return payload.get("results", {}).get("web", [])


def load_fixture(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        return payload.get("results", {}).get("web", payload.get("web", []))
    if isinstance(payload, list):
        return payload
    raise ValueError("Fixture must be a You.com response object or a list of web results.")
