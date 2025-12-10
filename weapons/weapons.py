""" Helpers to read weapons definitions from the standard installation. """

from pathlib import Path
from typing import Iterable, TextIO

from resources.resource_loader import load_resource


def _iter_weapon_lines(lines: Iterable[str]) -> Iterable[str]:
    for raw_line in lines:
        line = raw_line.strip()
        if line and not line.startswith("#"):
            yield line


def _parse_weapons(handle: TextIO) -> dict[str, list[str]]:
    weapons_list: dict[str, list[str]] = {}
    for line in _iter_weapon_lines(handle):
        token, *_ = line.split()
        aircraft, _, weapon = token.partition(".")
        weapons_list.setdefault(aircraft, []).append(weapon)
    return weapons_list


def read_weapons(root: str | Path) -> dict[str, list[str]]:
    """Return a mapping of aircraft class identifiers to their available weapons."""

    return load_resource(
        root,
        ("i18n", "weapons.properties"),
        _parse_weapons,
        "weapon definitions",
    )
