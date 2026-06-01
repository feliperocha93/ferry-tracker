from datetime import UTC, datetime

from core.models import FERRY_ROUTE_IDS, FerryRouteId, ScrapeStatus, WaitTimeObservation


def test_ferry_route_ids_count() -> None:
    assert len(FERRY_ROUTE_IDS) == 8


def test_ferry_route_id_values() -> None:
    assert FerryRouteId.SAO_SEBASTIAO_TO_ILHABELA == "sao_sebastiao_to_ilhabela"


def test_scrape_status_values() -> None:
    assert set(ScrapeStatus) == {
        ScrapeStatus.SUCCESS,
        ScrapeStatus.PARSE_ERROR,
        ScrapeStatus.SITE_DOWN,
    }


def test_wait_time_observation_table_name() -> None:
    assert WaitTimeObservation.__tablename__ == "wait_time_observations"


def test_wait_time_observation_unique_constraint() -> None:
    names = {c.name for c in WaitTimeObservation.__table__.constraints if hasattr(c, "name")}
    assert "uq_wait_time_observations_route_collected" in names


def test_wait_time_observation_instantiation() -> None:
    obs = WaitTimeObservation(
        ferry_route_id=FerryRouteId.SANTOS_TO_GUARUJA,
        collected_at=datetime(2026, 5, 30, 11, 0, tzinfo=UTC),
        wait_minutes=15,
        number_of_ships=4,
        scrape_status=ScrapeStatus.SUCCESS,
        raw_payload={"html": "<div/>"},
    )
    assert obs.wait_minutes == 15
    assert obs.scrape_status == "success"
