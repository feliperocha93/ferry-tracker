from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParsedRoute:
    ferry_route_id: str
    wait_minutes: int | None
    number_of_ships: int | None
    weather_alert: str | None
    parse_ok: bool
    error: str | None = None


@dataclass(frozen=True)
class ParseResult:
    routes: list[ParsedRoute] = field(default_factory=list)
    global_alert: str | None = None
