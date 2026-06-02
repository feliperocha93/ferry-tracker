"""Collection slot helpers (America/Sao_Paulo → UTC)."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

SAO_PAULO = ZoneInfo("America/Sao_Paulo")


def current_collection_slot(at: datetime | None = None) -> datetime:
    """Return the current :00 or :30 slot in São Paulo, as UTC."""
    if at is None:
        local = datetime.now(SAO_PAULO)
    elif at.tzinfo is None:
        local = at.replace(tzinfo=SAO_PAULO)
    else:
        local = at.astimezone(SAO_PAULO)

    minute = 0 if local.minute < 30 else 30
    slot_local = local.replace(minute=minute, second=0, microsecond=0)
    return slot_local.astimezone(UTC)
