from enum import StrEnum


class FerryRouteId(StrEnum):
    SAO_SEBASTIAO_TO_ILHABELA = "sao_sebastiao_to_ilhabela"
    ILHABELA_TO_SAO_SEBASTIAO = "ilhabela_to_sao_sebastiao"
    SANTOS_TO_GUARUJA = "santos_to_guaruja"
    GUARUJA_TO_SANTOS = "guaruja_to_santos"
    BERTIOGA_TO_GUARUJA = "bertioga_to_guaruja"
    GUARUJA_TO_BERTIOGA = "guaruja_to_bertioga"
    SANTOS_TO_VICENTE_DE_CARVALHO = "santos_to_vicente_de_carvalho"
    VICENTE_DE_CARVALHO_TO_SANTOS = "vicente_de_carvalho_to_santos"


FERRY_ROUTE_IDS: tuple[FerryRouteId, ...] = tuple(FerryRouteId)
