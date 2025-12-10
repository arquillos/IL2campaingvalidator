"""Helpers for loading stationary object definitions."""

from pathlib import Path
from typing import Iterable, TextIO

from resources.resource_loader import load_resource


STATIONARY_EXCLUDE_PREFIXES = ("//", "[", "#", ";")

def _iter_stationary_lines(lines: Iterable[str]) -> Iterable[str]:
    for raw_line in lines:
        line = raw_line.strip()
        if line and not line.startswith(STATIONARY_EXCLUDE_PREFIXES):
            yield line


def _parse_stationaries(handle: TextIO) -> dict[str, str]:
    stationaries: dict[str, str] = {}
    for line in _iter_stationary_lines(handle):
        name, identifier, *_ = line.split()
        stationaries[identifier] = name
    return stationaries


def read_stationaries(root: str | Path) -> dict[str, str]:
    """Read stationary class identifiers mapped to display names."""

    return load_resource(
        root,
        ("com", "maddox", "il2", "objects", "stationary.ini"),
        _parse_stationaries,
        "stationary definitions",
    )
