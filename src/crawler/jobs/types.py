from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ObservationRecord:
    ferry_route_id: str
    collected_at: datetime
    wait_minutes: int | None
    number_of_ships: int | None
    weather_alert: str | None
    scrape_status: str
    raw_payload: dict[str, Any] | None
