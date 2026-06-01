from enum import StrEnum


class ScrapeStatus(StrEnum):
    SUCCESS = "success"
    PARSE_ERROR = "parse_error"
    SITE_DOWN = "site_down"
