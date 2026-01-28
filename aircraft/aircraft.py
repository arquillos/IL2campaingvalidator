""" Aircraft related utilities """
from pathlib import Path
from typing import Iterator, TextIO

from resources.resource_loader import load_resource


AIRCRAFT_EXCLUDE_PREFIXES = ("[", "//", "*", "#", ";")


def iter_aircraft_lines(air_ini: Iterator[str]) -> Iterator[str]:
    """ Iterate over valid aircraft lines in air.ini """
    for raw_line in air_ini:
        line = raw_line.strip()
        if line and not line.startswith(AIRCRAFT_EXCLUDE_PREFIXES):
            yield line

def _parse_aircraft(handle: TextIO) -> dict[str, str]:
    aircraft_classes: dict[str, str] = {}

    for line in iter_aircraft_lines(handle):
        name, class_token, *_ = line.split()
        aircraft_classes[class_token[4:]] = name
    return aircraft_classes


def read_aircrafts(root: str | Path) -> dict[str, str]:
    """Read aircrafts and proper names."""

    return load_resource(
        root,
        ("com", "maddox", "il2", "objects", "air.ini"),
        _parse_aircraft,
        "aircraft classes",
    )
