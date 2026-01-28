"""
Squadrons related utilities
Get the squadrons from the STD/i18n/regInfo.propertie file 
"""

from pathlib import Path
from typing import Iterator, TextIO

from resources.resource_loader import load_resource


EXCLUDE_PREFIXES = "/"
SQUADRONS_FILE_NAME = "regInfo.properties"


def _iter_squadron_lines(squadrons_ini: Iterator[str]) -> Iterator[str]:
    """ Iterate over valid squadron lines """
    for raw_line in squadrons_ini:
        line = raw_line.strip()
        if line and not line.startswith(EXCLUDE_PREFIXES):
            yield line


def _parse_squadrons(handle: TextIO) -> list[str]:
    squadrons: list[str] = []

    for line in _iter_squadron_lines(handle):
        name = line.split()[0]
        squadrons.append(name)
    return squadrons


def read_squadrons(root: Path) -> list[str]:
    """Read squadrons from regInfo.properties"""

    return load_resource(
        root,
        ("i18n", SQUADRONS_FILE_NAME),
        _parse_squadrons,
        SQUADRONS_FILE_NAME,
    )
