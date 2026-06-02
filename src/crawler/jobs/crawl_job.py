"""Orchestrate fetch → parse → observation records."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from core.models.ferry_routes import FERRY_ROUTE_IDS
from core.models.scrape_status import ScrapeStatus
from core.utils.time_slots import current_collection_slot
from crawler.collectors.fetcher import FetchError, fetch_semil_page
from crawler.jobs.types import ObservationRecord
from crawler.parsers.semil_parser import parse_semil_html
from crawler.parsers.types import ParsedRoute, ParseResult

logger = logging.getLogger(__name__)

FetchFn = Callable[[], str]


@dataclass(frozen=True)
class CrawlJobResult:
    observations: list[ObservationRecord]
    global_alert: str | None
    fetch_failed: bool


def run_crawl(
    *,
    fetch_html: FetchFn | None = None,
    collected_at: datetime | None = None,
    html: str | None = None,
) -> CrawlJobResult:
    """Run one collection cycle and return 8 observation records."""
    slot = collected_at or current_collection_slot()
    fetch = fetch_html or fetch_semil_page
    logger.info("Starting crawl for slot %s", slot.isoformat())

    if html is not None:
        logger.info("Using provided HTML (%d chars)", len(html))
        return _build_from_html(html, slot)

    try:
        fetched = fetch()
    except FetchError:
        logger.error("SEMIL fetch failed; recording site_down for all routes")
        return CrawlJobResult(
            observations=_site_down_records(slot),
            global_alert=None,
            fetch_failed=True,
        )

    logger.info("Parsing SEMIL HTML (%d chars)", len(fetched))
    return _build_from_html(fetched, slot)


def _build_from_html(html: str, slot: datetime) -> CrawlJobResult:
    parsed = parse_semil_html(html)
    failure_payload = (
        _raw_payload(html, parsed.global_alert)
        if any(not route.parse_ok for route in parsed.routes)
        else None
    )
    raw_assigned = False
    observations: list[ObservationRecord] = []

    for route in parsed.routes:
        if route.parse_ok:
            observations.append(_observation_from_route(route, slot, raw_payload=None))
            continue

        payload = failure_payload if not raw_assigned else None
        raw_assigned = raw_assigned or payload is not None
        observations.append(_observation_from_route(route, slot, raw_payload=payload))

    result = CrawlJobResult(
        observations=observations,
        global_alert=parsed.global_alert,
        fetch_failed=False,
    )
    ok = sum(1 for obs in observations if obs.scrape_status == ScrapeStatus.SUCCESS)
    logger.info(
        "Crawl complete: %d/%d routes ok, global_alert=%s",
        ok,
        len(observations),
        "yes" if parsed.global_alert else "no",
    )
    return result


def _observation_from_route(
    route: ParsedRoute,
    slot: datetime,
    raw_payload: dict[str, Any] | None,
) -> ObservationRecord:
    if route.parse_ok:
        return ObservationRecord(
            ferry_route_id=route.ferry_route_id,
            collected_at=slot,
            wait_minutes=route.wait_minutes,
            number_of_ships=route.number_of_ships,
            weather_alert=route.weather_alert,
            scrape_status=ScrapeStatus.SUCCESS,
            raw_payload=None,
        )
    return ObservationRecord(
        ferry_route_id=route.ferry_route_id,
        collected_at=slot,
        wait_minutes=None,
        number_of_ships=None,
        weather_alert=route.weather_alert,
        scrape_status=ScrapeStatus.PARSE_ERROR,
        raw_payload=raw_payload,
    )


def _site_down_records(slot: datetime) -> list[ObservationRecord]:
    return [
        ObservationRecord(
            ferry_route_id=route_id.value,
            collected_at=slot,
            wait_minutes=None,
            number_of_ships=None,
            weather_alert=None,
            scrape_status=ScrapeStatus.SITE_DOWN,
            raw_payload=None,
        )
        for route_id in FERRY_ROUTE_IDS
    ]


def _raw_payload(html: str, global_alert: str | None) -> dict[str, Any]:
    payload: dict[str, Any] = {"html": html}
    if global_alert:
        payload["global_alert"] = global_alert
    return payload
