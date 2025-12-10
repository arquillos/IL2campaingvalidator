"""Helpers for working with chief.ini files."""

from pathlib import Path
from typing import Iterable, TextIO

from resources.resource_loader import load_resource


IGNORED_PREFIXES = (";", "[", "moveType", "/")

def _iter_chief_lines(lines: Iterable[str]) -> Iterable[str]:
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith(IGNORED_PREFIXES):
            continue
        if line.startswith("[Ships."):
            break
        yield line


def _parse_chiefs(handle: TextIO) -> list[str]:
    chiefs: list[str] = []
    for line in _iter_chief_lines(handle):
        chiefs.append(line.split()[0])
    return chiefs


def read_chiefs(root: str | Path) -> list[str]:
    """Return the chief identifiers defined before the ships section."""

    return load_resource(
        root,
        ("com", "maddox", "il2", "objects", "chief.ini"),
        _parse_chiefs,
        "chief definitions",
    )
