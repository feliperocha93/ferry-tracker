from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, Index, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class WaitTimeObservation(Base):
    __tablename__ = "wait_time_observations"
    __table_args__ = (
        UniqueConstraint(
            "ferry_route_id",
            "collected_at",
            name="uq_wait_time_observations_route_collected",
        ),
        Index("ix_wait_time_observations_collected_at", "collected_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ferry_route_id: Mapped[str] = mapped_column(Text, nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    wait_minutes: Mapped[int | None] = mapped_column(nullable=True)
    number_of_ships: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    weather_alert: Mapped[str | None] = mapped_column(Text, nullable=True)
    scrape_status: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
