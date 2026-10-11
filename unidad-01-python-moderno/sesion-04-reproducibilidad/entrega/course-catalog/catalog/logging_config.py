"""Configure application logs without writing to protocol stdout."""

import logging
from pathlib import Path


def configure_logging(level: str = "INFO", log_file: Path | None = None) -> None:
    formatter = logging.Formatter("%(levelname)s | %(name)s | %(message)s")
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    # Replace handlers when the SDK has already configured the root logger.
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()
    root.addHandler(console)
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
