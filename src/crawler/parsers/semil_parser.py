"""Parse SEMIL HTML crossing summary widget (menu-trav panels)."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

from core.models.ferry_routes import FERRY_ROUTE_IDS, FerryRouteId
from crawler.parsers.types import ParsedRoute, ParseResult

# href slug -> (route for terminal A, route for terminal B)
MONITORED_CROSSINGS: dict[str, tuple[FerryRouteId, FerryRouteId]] = {
    "sao-sebastiao-ilhabela": (
        FerryRouteId.SAO_SEBASTIAO_TO_ILHABELA,
        FerryRouteId.ILHABELA_TO_SAO_SEBASTIAO,
    ),
    "santos-guaruja": (
        FerryRouteId.SANTOS_TO_GUARUJA,
        FerryRouteId.GUARUJA_TO_SANTOS,
    ),
    "bertioga-guaruja": (
        FerryRouteId.BERTIOGA_TO_GUARUJA,
        FerryRouteId.GUARUJA_TO_BERTIOGA,
    ),
    "santos-vicente-de-carvalho": (
        FerryRouteId.SANTOS_TO_VICENTE_DE_CARVALHO,
        FerryRouteId.VICENTE_DE_CARVALHO_TO_SANTOS,
    ),
}


def parse_semil_html(html: str) -> ParseResult:
    soup = BeautifulSoup(html, "html.parser")
    global_alert = _extract_global_alert(soup)
    parsed_by_id: dict[str, ParsedRoute] = {}

    for item in soup.select("li.menu-item.menu-trav"):
        crossing = _parse_menu_item(item)
        if crossing is None:
            continue
        parsed_by_id[crossing[0].ferry_route_id] = crossing[0]
        parsed_by_id[crossing[1].ferry_route_id] = crossing[1]

    routes: list[ParsedRoute] = []
    for route_id in FERRY_ROUTE_IDS:
        if route_id.value in parsed_by_id:
            routes.append(parsed_by_id[route_id.value])
        else:
            routes.append(
                ParsedRoute(
                    ferry_route_id=route_id.value,
                    wait_minutes=None,
                    number_of_ships=None,
                    weather_alert=None,
                    parse_ok=False,
                    error=f"Missing data for {route_id.value}",
                )
            )

    return ParseResult(routes=routes, global_alert=global_alert)


def _extract_global_alert(soup: BeautifulSoup) -> str | None:
    popup = soup.select_one(".popuptrav")
    if popup:
        text = popup.get_text(" ", strip=True)
        if text:
            return text

    for node in soup.find_all(string=re.compile(r"instabilidade", re.I)):
        text = str(node).strip()
        if len(text) > 40:
            return text
    return None


def _parse_menu_item(item: Tag) -> tuple[ParsedRoute, ParsedRoute] | None:
    link = item.select_one("a.menu-link")
    if link is None:
        return None

    slug = _href_slug(link.get("href", ""))
    if slug is None or slug not in MONITORED_CROSSINGS:
        return None

    route_a, route_b = MONITORED_CROSSINGS[slug]
    wait_a = _minutes(item, "menu-travMinutosA")
    wait_b = _minutes(item, "menu-travMinutosB")
    ships = _ships(item)
    weather = _weather(item)

    if wait_a is None or wait_b is None:
        error = f"Could not parse wait times for {slug}"
        return (
            ParsedRoute(
                ferry_route_id=route_a.value,
                wait_minutes=None,
                number_of_ships=None,
                weather_alert=weather,
                parse_ok=False,
                error=error,
            ),
            ParsedRoute(
                ferry_route_id=route_b.value,
                wait_minutes=None,
                number_of_ships=None,
                weather_alert=weather,
                parse_ok=False,
                error=error,
            ),
        )

    route_row_a = ParsedRoute(
        ferry_route_id=route_a.value,
        wait_minutes=wait_a,
        number_of_ships=ships,
        weather_alert=weather,
        parse_ok=True,
    )
    route_row_b = ParsedRoute(
        ferry_route_id=route_b.value,
        wait_minutes=wait_b,
        number_of_ships=ships,
        weather_alert=weather,
        parse_ok=True,
    )
    return route_row_a, route_row_b


def _href_slug(href: str) -> str | None:
    if not href:
        return None
    path = urlparse(href).path.strip("/")
    if not path:
        return None
    return path.split("/")[-1]


def _minutes(item: Tag, strong_id_prefix: str) -> int | None:
    strong = item.find("strong", id=re.compile(rf"^{re.escape(strong_id_prefix)}"))
    if strong is None:
        return None
    return _parse_int(strong.get_text(strip=True))


def _ships(item: Tag) -> int | None:
    num = item.select_one("td[id^='menu-embarcacao'] strong.num")
    if num is None:
        return None
    return _parse_int(num.get_text(strip=True))


def _weather(item: Tag) -> str | None:
    icon = item.find("i", id=re.compile(r"^menu-tempoClima"))
    if icon is None:
        return None
    title = icon.get("title")
    if title:
        return str(title).strip()
    classes = icon.get("class") or []
    for cls in classes:
        if cls.startswith("minitrav-"):
            return cls.removeprefix("minitrav-").replace("-", " ")
    return None


def _parse_int(value: str) -> int | None:
    value = value.strip()
    if not value.isdigit():
        return None
    return int(value)
