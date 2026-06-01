from __future__ import annotations

import httpx
import pytest

from crawler.collectors.fetcher import FetchError, fetch_html
from crawler.parsers.semil_parser import parse_semil_html


def test_fetch_html_retries_then_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    with pytest.raises(FetchError):
        fetch_html("https://example.com/page", client=client, retry_backoff=0)


@pytest.mark.integration
def test_fetch_and_parse_live_semil_page() -> None:
    """Optional live check — skip in CI with: pytest -m 'not integration'."""
    html = fetch_html(
        "https://semil.sp.gov.br/travessias/travessias-automoveis/sao-sebastiao-ilhabela/",
        retry_backoff=0,
    )
    result = parse_semil_html(html)
    assert len(result.routes) == 8
    assert sum(1 for r in result.routes if r.parse_ok) >= 4
