"""CLI entry point for the crawl job."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from crawler.collectors.fetcher import FetchError, fetch_semil_page
from crawler.parsers.semil_parser import parse_semil_html


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect ferry wait times from SEMIL.")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Fetch and persist observations to the database (phase 0.5)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and print parsed routes as JSON (default)",
    )
    parser.add_argument(
        "--html-file",
        metavar="PATH",
        help="Parse a local HTML file instead of fetching the live site",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.save:
        print("Persist not yet implemented (phase 0.5).", file=sys.stderr)
        return 1

    try:
        html = _load_html(args.html_file)
    except FetchError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    result = parse_semil_html(html)
    payload = {
        "global_alert": result.global_alert,
        "routes": [asdict(route) for route in result.routes],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if any(not route.parse_ok for route in result.routes):
        return 1
    return 0


def _load_html(html_file: str | None) -> str:
    if html_file:
        return open(html_file, encoding="utf-8").read()
    return fetch_semil_page()


if __name__ == "__main__":
    raise SystemExit(main())
