"""Helpers for loading static object identifiers."""

from pathlib import Path
from typing import Iterable, TextIO

from resources.resource_loader import load_resource


def _iter_object_lines(lines: Iterable[str]) -> Iterable[str]:
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("[b"):
            yield line


def _parse_objects(handle: TextIO) -> list[str]:
    objects: list[str] = []
    for line in _iter_object_lines(handle):
        objects.append(line[11:-1])
    return objects


def read_objects(root: str | Path) -> list[str]:
    """Return the list of static object identifiers."""

    return load_resource(
        root,
        ("com", "maddox", "il2", "objects", "static.ini"),
        _parse_objects,
        "static objects",
    )
