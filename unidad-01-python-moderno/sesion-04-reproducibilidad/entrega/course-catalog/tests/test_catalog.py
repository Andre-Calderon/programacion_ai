import json
from pathlib import Path

import pytest

from catalog.search import search_courses


def test_case_and_spaces() -> None:
    assert [course.code for course in search_courses(" PYTHON ")] == ["PY01", "PY02"]


def test_no_match_is_valid() -> None:
    assert search_courses("astronomy") == []


def test_empty_query() -> None:
    with pytest.raises(ValueError, match="blank"):
        search_courses("   ")


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        search_courses("python", tmp_path / "missing.json")


def test_invalid_course(tmp_path: Path) -> None:
    path = tmp_path / "courses.json"
    path.write_text(json.dumps([{"code": "X", "title": "Python", "hours": 0}]))
    with pytest.raises(ValueError):
        search_courses("python", path)
