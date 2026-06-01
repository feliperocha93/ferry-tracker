"""HTTP fetcher for SEMIL travessias pages."""

from __future__ import annotations

import time

import httpx

SEMIL_COLLECTION_URL = (
    "https://semil.sp.gov.br/travessias/travessias-automoveis/sao-sebastiao-ilhabela/"
)
DEFAULT_USER_AGENT = "ferry-wait/0.1 (+https://github.com/; data collection)"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_RETRY_BACKOFF_SECONDS = 30.0


class FetchError(Exception):
    """Raised when the page cannot be fetched after retries."""


def fetch_html(
    url: str = SEMIL_COLLECTION_URL,
    *,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    retry_backoff: float = DEFAULT_RETRY_BACKOFF_SECONDS,
    client: httpx.Client | None = None,
) -> str:
    """GET *url* and return response text. Retries once after *retry_backoff* seconds."""
    headers = {"User-Agent": DEFAULT_USER_AGENT}

    if client is not None:
        return _fetch_with_client(
            client, url, headers, retry_backoff=retry_backoff
        )

    with httpx.Client(timeout=timeout, follow_redirects=True) as owned:
        return _fetch_with_client(
            owned, url, headers, retry_backoff=retry_backoff
        )


def fetch_semil_page(**kwargs: object) -> str:
    """Fetch the canonical SEMIL page used for all crossing summaries."""
    return fetch_html(SEMIL_COLLECTION_URL, **kwargs)  # type: ignore[arg-type]


def _fetch_with_client(
    client: httpx.Client,
    url: str,
    headers: dict[str, str],
    *,
    retry_backoff: float = DEFAULT_RETRY_BACKOFF_SECONDS,
) -> str:
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(retry_backoff)
    msg = f"Failed to fetch {url}"
    raise FetchError(msg) from last_error
