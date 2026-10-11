.PHONY: check lint format-check types format test run sync server client

check: lint format-check types test

lint:
	uv run --locked ruff check .

format-check:
	uv run --locked ruff format --check .

types:
	uv run --locked mypy --strict main.py server.py client.py catalog

format:
	uv run --locked ruff format .

test:
	uv run --locked python -m pytest

run:
	uv run --locked python main.py python

sync:
	uv sync --locked

server:
	uv run --locked python server.py

client:
	uv run --locked python client.py python
