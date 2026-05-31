"""CLI entry point for the crawl job (full implementation in phase 0.4)."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect ferry wait times from SEMIL.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and print observations without persisting (default)",
    )
    group.add_argument(
        "--save",
        action="store_true",
        help="Fetch and persist observations to the database",
    )
    parser.parse_args(argv if argv is not None else sys.argv[1:])

    print("Crawl job not yet implemented (phase 0.4).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
