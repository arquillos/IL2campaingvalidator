"""Dataclasses representing mission-level information."""

from dataclasses import dataclass
from pathlib import Path
from typing import FrozenSet, Tuple


@dataclass(frozen=True)
class MissionDate:
    """Mission date components extracted from a mission file."""

    year: str
    month: str
    day: str


@dataclass(frozen=True)
class MissionAircraft:
    """Aircraft assignment for a wing in a mission."""

    aircraft_code: str
    weapon_code: str
    skins: FrozenSet[str]


@dataclass(frozen=True)
class MissionData:
    """Aggregated mission data used by the analyzer."""

    path: Path
    map_name: str | None
    date: MissionDate | None
    date_is_custom: bool
    player_squadron: str
    aircraft: Tuple[MissionAircraft, ...]
    chiefs: FrozenSet[str]
    stationaries: FrozenSet[str]
    buildings: Tuple[str, ...]
    wing_sections: Tuple[str, ...]
    stat_planes_without_markings: Tuple[str, ...]
