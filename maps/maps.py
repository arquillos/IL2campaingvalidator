"""
Maps related utilities
Get the maps from the MODS\MAPMODS\Maps\all.ini
"""

from pathlib import Path
from typing import Iterator, TextIO

from resources.resource_loader import load_resource

EXCLUDE_PREFIXES = (";", "[")
MAPS_FILE_NAME = "all.ini"


def _iter_map_lines(maps_ini: Iterator[str]) -> Iterator[str]:
    """ Iterate over valid map lines """
    for raw_line in maps_ini:
        line = raw_line.strip()
        if line and not line.startswith(EXCLUDE_PREFIXES):
            yield line


def _parse_maps(handle: TextIO) -> list[str]:
    """
    Collect the maps from the file

    Example:
        Norway	Norway/load.ini

        Output: Norway/load.ini
    """
    maps: list[str] = []

    for line in _iter_map_lines(handle):
        splitted_line = line.split()
        # Take the second column of the line
        if len(splitted_line) > 1:
            name = splitted_line[1]
            maps.append(name)
    return maps


def read_maps(root: Path) -> list[str]:
    """Read maps from all.ini file """

    return load_resource(
        root,
        ("Maps", MAPS_FILE_NAME),
        _parse_maps,
        MAPS_FILE_NAME,
    )
