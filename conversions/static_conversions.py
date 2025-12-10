"""Helpers for loading conversion mappings."""

import logging

from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


def _parse_conversion_line(line: str) -> tuple[str, str] | None:
    """Parse a conversion entry. Returns None for blank/comment lines."""

    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    parts = [part.strip() for part in stripped.split(",", maxsplit=1)]
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Invalid conversion line: {line!r}")

    return parts[0], parts[1]


def _iter_conversion_entries(lines: Iterable[str]) -> Iterable[tuple[str, str]]:
    for line in lines:
        result = _parse_conversion_line(line)
        if result is not None:
            yield result


def read_conversion_file(root: str | Path) -> dict[str, str]:
    """Read the common conversions from the conversion file."""

    conversion_path = Path(root) / "config" / "Common Conversions.txt"
    conversion_db: dict[str, str] = {}

    with conversion_path.open(encoding="utf-8") as handle:
        for source, target in _iter_conversion_entries(handle):
            conversion_db[source] = target

    logger.debug("Loaded %d conversion entries", len(conversion_db))
    logger.debug("Conversion entries: %s", conversion_db)
    return conversion_db
