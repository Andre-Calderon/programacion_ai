"""Query the catalog directly from the terminal."""

import argparse
import json
import logging
from pathlib import Path

from catalog.logging_config import configure_logging
from catalog.search import DEFAULT_CATALOG, search_courses


def main() -> int:
    parser = argparse.ArgumentParser(description="Search the course catalog")
    parser.add_argument("query")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
    )
    parser.add_argument("--log-file", type=Path)
    args = parser.parse_args()
    configure_logging(args.log_level, args.log_file)
    try:
        courses = search_courses(args.query, args.catalog)
    except (OSError, ValueError):
        logging.getLogger(__name__).exception("Catalog search failed")
        return 1
    print(json.dumps([course.model_dump() for course in courses], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
