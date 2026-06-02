"""CLI entry point for the crawl job."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from datetime import datetime

from core.database.repository import save_observations
from crawler.collectors.fetcher import FetchError, fetch_semil_page
from crawler.jobs.crawl_job import CrawlJobResult, run_crawl

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect ferry wait times from SEMIL.")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Fetch and persist observations to the database",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and print observation records as JSON (default without --save)",
    )
    parser.add_argument(
        "--html-file",
        metavar="PATH",
        help="Parse a local HTML file instead of fetching the live site",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    _configure_logging()
    logger.info(
        "Crawl job started (save=%s, dry_run=%s, html_file=%s)",
        args.save,
        args.dry_run,
        args.html_file,
    )

    try:
        result = _execute_crawl(args.html_file)
    except FetchError:
        logger.exception("Fetch failed")
        return 1
    except OSError:
        logger.exception("I/O error")
        return 1
    except RuntimeError:
        logger.exception("Runtime error")
        return 1

    save_result = None
    if args.save:
        save_result = save_observations(result.observations)

    print(json.dumps(_payload(result, save_result), ensure_ascii=False, indent=2))
    exit_code = _exit_code(result)
    logger.info("Crawl job finished with exit code %d", exit_code)
    return exit_code


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


def _execute_crawl(html_file: str | None) -> CrawlJobResult:
    if html_file:
        html = open(html_file, encoding="utf-8").read()
        return run_crawl(html=html)
    return run_crawl(fetch_html=fetch_semil_page)


def _payload(result: CrawlJobResult, save_result: object | None) -> dict[str, object]:
    data: dict[str, object] = {
        "collected_at": _iso(result.observations[0].collected_at),
        "global_alert": result.global_alert,
        "fetch_failed": result.fetch_failed,
        "observations": [_observation_dict(obs) for obs in result.observations],
    }
    if save_result is not None:
        data["save"] = asdict(save_result)
    return data


def _exit_code(result: CrawlJobResult) -> int:
    if result.fetch_failed:
        return 1
    if any(obs.scrape_status != "success" for obs in result.observations):
        return 1
    return 0


def _observation_dict(obs: object) -> dict[str, object]:
    data = asdict(obs)
    collected_at = data.pop("collected_at")
    data["collected_at"] = _iso(collected_at)
    raw = data.get("raw_payload")
    if isinstance(raw, dict) and "html" in raw:
        data["raw_payload"] = {
            **raw,
            "html": f"<{len(raw['html'])} chars>",
        }
    return data


def _iso(dt: datetime) -> str:
    return dt.isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
