"""Integration tests — require local PostgreSQL (DATABASE_URL + migrations)."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import delete, func, select

from core.database.env import load_dotenv
from core.database.repository import save_observations
from core.database.session import get_session
from core.models.scrape_status import ScrapeStatus
from core.models.wait_time_observation import WaitTimeObservation
from crawler.jobs.crawl_job import run_crawl

FIXTURE = Path(__file__).resolve().parents[1] / "parsers" / "fixtures" / "semil_sample.html"
TEST_SLOT = datetime(2099, 6, 1, 15, 0, tzinfo=UTC)


@pytest.fixture(scope="module")
def db_available() -> None:
    load_dotenv()
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set")

    session = get_session()
    try:
        session.execute(select(func.count()).select_from(WaitTimeObservation))
        session.commit()
    except Exception as exc:
        pytest.skip(f"PostgreSQL unavailable: {exc}")
    finally:
        session.close()


@pytest.fixture
def db_session(db_available: None):
    session = get_session()
    yield session
    session.close()


@pytest.fixture
def clean_test_slot(db_session):
    db_session.execute(
        delete(WaitTimeObservation).where(WaitTimeObservation.collected_at == TEST_SLOT)
    )
    db_session.commit()
    yield TEST_SLOT
    db_session.execute(
        delete(WaitTimeObservation).where(WaitTimeObservation.collected_at == TEST_SLOT)
    )
    db_session.commit()


@pytest.fixture
def sample_html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.mark.integration_db
def test_save_successful_crawl(db_session, clean_test_slot, sample_html: str) -> None:
    result = run_crawl(html=sample_html, collected_at=clean_test_slot)

    save = save_observations(result.observations, session=db_session)
    db_session.commit()

    assert save.inserted == 8
    assert save.skipped == 0

    count = db_session.scalar(
        select(func.count())
        .select_from(WaitTimeObservation)
        .where(WaitTimeObservation.collected_at == clean_test_slot)
    )
    assert count == 8

    raw_count = db_session.scalar(
        select(func.count())
        .select_from(WaitTimeObservation)
        .where(
            WaitTimeObservation.collected_at == clean_test_slot,
            WaitTimeObservation.raw_payload.has_key("html"),
        )
    )
    assert raw_count == 0


@pytest.mark.integration_db
def test_save_is_idempotent(db_session, clean_test_slot, sample_html: str) -> None:
    result = run_crawl(html=sample_html, collected_at=clean_test_slot)

    first = save_observations(result.observations, session=db_session)
    db_session.commit()
    assert first.inserted == 8

    second = save_observations(result.observations, session=db_session)
    db_session.commit()
    assert second.inserted == 0
    assert second.skipped == 8

    count = db_session.scalar(
        select(func.count())
        .select_from(WaitTimeObservation)
        .where(WaitTimeObservation.collected_at == clean_test_slot)
    )
    assert count == 8


@pytest.mark.integration_db
def test_save_parse_error_stores_raw_payload_once(db_session, clean_test_slot) -> None:
    html = """
    <html><body>
    <div class="popuptrav"><p>Sistema com instabilidade.</p></div>
    </body></html>
    """
    result = run_crawl(html=html, collected_at=clean_test_slot)

    save = save_observations(result.observations, session=db_session)
    db_session.commit()

    assert save.inserted == 8
    assert all(obs.scrape_status == ScrapeStatus.PARSE_ERROR for obs in result.observations)

    raw_count = db_session.scalar(
        select(func.count())
        .select_from(WaitTimeObservation)
        .where(
            WaitTimeObservation.collected_at == clean_test_slot,
            WaitTimeObservation.raw_payload.has_key("html"),
        )
    )
    assert raw_count == 1
