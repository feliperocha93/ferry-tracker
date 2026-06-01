from __future__ import annotations

from pathlib import Path

import pytest

from core.models.ferry_routes import FERRY_ROUTE_IDS, FerryRouteId
from crawler.parsers.semil_parser import parse_semil_html

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "parsers" / "fixtures" / "semil_sample.html"


@pytest.fixture
def sample_html() -> str:
    return FIXTURE_PATH.read_text(encoding="utf-8")


def test_parses_eight_monitored_routes(sample_html: str) -> None:
    result = parse_semil_html(sample_html)

    assert len(result.routes) == 8
    assert {r.ferry_route_id for r in result.routes} == {rid.value for rid in FERRY_ROUTE_IDS}
    assert all(r.parse_ok for r in result.routes)


def test_sao_sebastiao_ilhabela_wait_times(sample_html: str) -> None:
    result = parse_semil_html(sample_html)
    by_id = {r.ferry_route_id: r for r in result.routes}

    assert by_id[FerryRouteId.SAO_SEBASTIAO_TO_ILHABELA].wait_minutes == 30
    assert by_id[FerryRouteId.ILHABELA_TO_SAO_SEBASTIAO].wait_minutes == 30
    assert by_id[FerryRouteId.SAO_SEBASTIAO_TO_ILHABELA].number_of_ships == 2


def test_santos_guaruja_wait_times(sample_html: str) -> None:
    result = parse_semil_html(sample_html)
    by_id = {r.ferry_route_id: r for r in result.routes}

    assert by_id[FerryRouteId.SANTOS_TO_GUARUJA].wait_minutes == 30
    assert by_id[FerryRouteId.GUARUJA_TO_SANTOS].wait_minutes == 15
    assert by_id[FerryRouteId.SANTOS_TO_GUARUJA].number_of_ships == 7


def test_weather_alert_per_crossing(sample_html: str) -> None:
    result = parse_semil_html(sample_html)
    by_id = {r.ferry_route_id: r for r in result.routes}

    assert by_id[FerryRouteId.SANTOS_TO_GUARUJA].weather_alert == "parcialmente-nublado"


def test_global_instability_alert(sample_html: str) -> None:
    result = parse_semil_html(sample_html)

    assert result.global_alert is not None
    assert "instabilidade" in result.global_alert.lower()


def test_missing_monitored_crossing_marks_parse_error() -> None:
    html = """
    <html><body>
    <li class="menu-item menu-trav">
      <a class="menu-link" href="/travessias/travessias-automoveis/santos-guaruja/">
        <strong id="menu-travMinutosA-1">10</strong>
        <strong id="menu-travMinutosB-1">20</strong>
        <strong class="num">3</strong>
      </a>
    </li>
    </body></html>
    """
    result = parse_semil_html(html)
    failed = [r for r in result.routes if not r.parse_ok]

    assert len(failed) == 6
    assert all(r.wait_minutes is None for r in failed)


def test_broken_menu_item_marks_pair_as_parse_error() -> None:
    html = """
    <html><body>
    <li class="menu-item menu-trav">
      <a class="menu-link" href="/travessias/travessias-automoveis/sao-sebastiao-ilhabela/">
        <span id="menu-travessia-a-1">SÃO SEBASTIÃO</span>
      </a>
    </li>
    </body></html>
    """
    result = parse_semil_html(html)
    by_id = {r.ferry_route_id: r for r in result.routes}

    assert not by_id[FerryRouteId.SAO_SEBASTIAO_TO_ILHABELA].parse_ok
    assert not by_id[FerryRouteId.ILHABELA_TO_SAO_SEBASTIAO].parse_ok
