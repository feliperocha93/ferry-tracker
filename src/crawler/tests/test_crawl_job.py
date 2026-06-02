from datetime import UTC, datetime
from pathlib import Path

import pytest

from core.models.ferry_routes import FerryRouteId
from core.models.scrape_status import ScrapeStatus
from crawler.collectors.fetcher import FetchError
from crawler.jobs.crawl_job import run_crawl

FIXTURE = Path(__file__).resolve().parents[1] / "parsers" / "fixtures" / "semil_sample.html"
SLOT = datetime(2026, 5, 30, 13, 0, tzinfo=UTC)


@pytest.fixture
def sample_html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_successful_crawl_from_html(sample_html: str) -> None:
    result = run_crawl(html=sample_html, collected_at=SLOT)

    assert len(result.observations) == 8
    assert not result.fetch_failed
    assert all(obs.collected_at == SLOT for obs in result.observations)
    assert all(obs.scrape_status == ScrapeStatus.SUCCESS for obs in result.observations)
    assert all(obs.wait_minutes is not None for obs in result.observations)
    assert all(obs.raw_payload is None for obs in result.observations)


def test_success_exposes_global_alert_at_job_level(sample_html: str) -> None:
    result = run_crawl(html=sample_html, collected_at=SLOT)

    assert result.global_alert is not None
    assert "instabilidade" in result.global_alert.lower()


def test_site_down_when_fetch_fails() -> None:
    def fail() -> str:
        raise FetchError("down")

    result = run_crawl(fetch_html=fail, collected_at=SLOT)

    assert result.fetch_failed
    assert len(result.observations) == 8
    assert all(obs.scrape_status == ScrapeStatus.SITE_DOWN for obs in result.observations)
    assert all(obs.wait_minutes is None for obs in result.observations)
    assert all(obs.raw_payload is None for obs in result.observations)


def test_parse_error_stores_raw_payload_once() -> None:
    html = "<html><body>no widget</body></html>"
    result = run_crawl(html=html, collected_at=SLOT)

    assert not result.fetch_failed
    assert all(obs.scrape_status == ScrapeStatus.PARSE_ERROR for obs in result.observations)

    with_payload = [obs for obs in result.observations if obs.raw_payload is not None]
    assert len(with_payload) == 1
    assert with_payload[0].ferry_route_id == FerryRouteId.SAO_SEBASTIAO_TO_ILHABELA
    assert "html" in with_payload[0].raw_payload

    without_payload = [obs for obs in result.observations if obs.raw_payload is None]
    assert len(without_payload) == 7


def test_parse_error_includes_global_alert_in_single_raw_payload() -> None:
    html = """
    <html><body>
    <div class="popuptrav"><p>Sistema com instabilidade no site.</p></div>
    </body></html>
    """
    result = run_crawl(html=html, collected_at=SLOT)

    with_payload = [obs for obs in result.observations if obs.raw_payload is not None]
    assert len(with_payload) == 1
    assert with_payload[0].raw_payload is not None
    assert "instabilidade" in with_payload[0].raw_payload["global_alert"].lower()
