"""Persistence helpers for wait time observations."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from core.database.session import get_session
from core.models.wait_time_observation import WaitTimeObservation
from crawler.jobs.types import ObservationRecord

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SaveResult:
    inserted: int
    skipped: int


def save_observations(
    records: list[ObservationRecord],
    *,
    session: Session | None = None,
) -> SaveResult:
    """Insert observations; skip rows that violate the unique constraint."""
    if not records:
        logger.info("No observations to save")
        return SaveResult(inserted=0, skipped=0)

    logger.info("Saving %d observation(s) to database", len(records))
    own_session = session is None
    db = session or get_session()
    try:
        rows = [_record_to_row(record) for record in records]
        stmt = insert(WaitTimeObservation).values(rows)
        stmt = stmt.on_conflict_do_nothing(
            constraint="uq_wait_time_observations_route_collected",
        ).returning(WaitTimeObservation.id)
        inserted_rows = db.execute(stmt).fetchall()
        inserted = len(inserted_rows)
        if own_session:
            db.commit()
        result = SaveResult(inserted=inserted, skipped=len(records) - inserted)
        logger.info(
            "Save complete: inserted=%d skipped=%d",
            result.inserted,
            result.skipped,
        )
        return result
    except Exception:
        logger.exception("Failed to save observations")
        if own_session:
            db.rollback()
        raise
    finally:
        if own_session:
            db.close()


def _record_to_row(record: ObservationRecord) -> dict[str, object]:
    return {
        "ferry_route_id": record.ferry_route_id,
        "collected_at": record.collected_at,
        "wait_minutes": record.wait_minutes,
        "number_of_ships": record.number_of_ships,
        "weather_alert": record.weather_alert,
        "scrape_status": str(record.scrape_status),
        "raw_payload": record.raw_payload,
    }
