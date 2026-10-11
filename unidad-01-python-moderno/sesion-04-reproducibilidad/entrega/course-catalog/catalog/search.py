"""Read and search a small course catalog."""

import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "data" / "courses.json"


class Course(BaseModel):
    code: str
    title: str
    hours: int = Field(gt=0)


def search_courses(query: str, path: Path = DEFAULT_CATALOG) -> list[Course]:
    """Find courses whose titles contain the query, ignoring letter case."""
    term = query.strip().casefold()
    if not term:
        raise ValueError("Query must not be blank")
    logger.debug("Reading catalog: %s", path)
    with path.open(encoding="utf-8") as source:
        records = json.load(source)
    if not isinstance(records, list):
        raise ValueError("Catalog must contain a JSON list")
    courses = [Course.model_validate(record) for record in records]
    matches = []
    for course in courses:
        if term in course.title.casefold():
            matches.append(course)
    logger.info(
        "Search completed: %d matches out of %d courses read",
        len(matches),
        len(courses),
    )
    return matches
