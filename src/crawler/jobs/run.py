"""CLI entry point for the crawl job."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime

from core.database.repository import save_observations
from crawler.collectors.fetcher import FetchError, fetch_semil_page
from crawler.jobs.crawl_job import CrawlJobResult, run_crawl


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

    try:
        result = _execute_crawl(args.html_file)
    except FetchError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    save_result = None
    if args.save:
        save_result = save_observations(result.observations)

    print(json.dumps(_payload(result, save_result), ensure_ascii=False, indent=2))
    return _exit_code(result)


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
