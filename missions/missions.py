"""Helpers for reading campaign mission listings."""

import logging

from pathlib import Path
from typing import Iterable

from .mission_data import MissionAircraft, MissionData, MissionDate


logger = logging.getLogger(__name__)


def _iter_mission_tokens(lines: Iterable[str]) -> Iterable[str]:
    for raw_line in lines:
        for token in raw_line.split():
            if token.lower().endswith(".mis"):
                yield token.rstrip()


def read_missions(root: str | Path) -> list[Path]:
    """Return the list of mission file paths defined in campaign.ini."""

    root_path = Path(root)
    campaign_ini_path = root_path / "campaign.ini"
    logger.info("Loading missions from %s", campaign_ini_path)

    mission_paths: list[Path] = []

    try:
        with campaign_ini_path.open(encoding="utf-8") as handle:
            for token in _iter_mission_tokens(handle):
                mission_paths.append(root_path / token)
    except FileNotFoundError:
        logger.exception("campaign.ini not found at %s", campaign_ini_path)
        raise

    logger.debug("Discovered %d missions", len(mission_paths))
    return mission_paths

def read_mission(mission_path: str | Path) -> MissionData:
    """Read a mission file and extract relevant data."""

    path = Path(mission_path)
    logger.info("Reading mission file %s", path)

    # Read all lines from the mission file
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        logger.exception("Mission file not found: %s", path)
        raise

    aircraft_entries: list[MissionAircraft] = []
    stat_planes_without_markings: list[str] = []
    chiefs_list: set[str] = set()
    stationaries_list: set[str] = set()
    buildings_list: list[str] = []
    wing_sections: list[str] = []

    player_sqdn = ""
    map_name: str | None = None
    date_year: str | None = None
    date_month: str | None = None
    date_day: str | None = None
    date_is_custom = False

    idx = 0
    total_lines = len(lines)

    while idx < total_lines:
        raw_line = lines[idx]

        # Strip whitespace and convert to lowercase
        stripped = raw_line.strip()
        lower_line = stripped.lower()
        idx += 1

        if not stripped:
            continue

        if "player " in lower_line:
            tokens = stripped.split()
            if len(tokens) > 1:
                player_sqdn = tokens[1]
                logger.debug("Player squadron detected: %s", player_sqdn)
            continue

        if lower_line == "[main]":
            if idx < total_lines:
                map_tokens = lines[idx].strip().split()
                if len(map_tokens) > 1:
                    map_name = map_tokens[1]
                    logger.debug("Mission map detected: %s", map_name)
                else:
                    logger.warning("[Main] section missing map entry in %s", path.name)
            else:
                logger.warning("[Main] section incomplete near end of file in %s", path.name)
            idx += 1
            continue

        if lower_line == "[season]":
            if idx + 2 < total_lines:
                year_line = lines[idx].strip()
                month_line = lines[idx + 1].strip()
                day_line = lines[idx + 2].strip()

                date_year = year_line[5:] if len(year_line) >= 5 else ""
                date_month = month_line[6:] if len(month_line) >= 6 else ""
                date_day = day_line[4:] if len(day_line) >= 4 else ""

                if not (date_year == "1940" and date_month == "7" and date_day == "10"):
                    date_is_custom = True

                logger.debug("Mission date: %s-%s-%s", date_year, date_month, date_day)
            else:
                logger.warning("[Season] section incomplete in %s", path.name)
            idx += 3
            continue

        if lower_line == "[wing]":
            while idx < total_lines:
                candidate = lines[idx].strip()
                if not candidate:
                    idx += 1
                    continue
                if candidate.startswith("["):
                    break
                if candidate not in wing_sections:
                    wing_sections.append(candidate)
                    logger.debug("Registered wing section %s", candidate)
                idx += 1
            continue

        if stripped.startswith("[") and stripped.endswith("]"):
            section_name = stripped[1:-1]
            if section_name in wing_sections:
                skin_set: set[str] = set()
                aircraft_code = ""

                while idx < total_lines:
                    detail = lines[idx].strip()
                    if not detail:
                        idx += 1
                        continue
                    if detail.startswith("["):
                        break

                    lower_detail = detail.lower()
                    if lower_detail.startswith("skin"):
                        parts = detail.split(maxsplit=1)
                        if len(parts) == 2:
                            skin_set.add(parts[1])
                    elif lower_detail.startswith("class"):
                        parts = detail.split(maxsplit=1)
                        raw_value = parts[1] if len(parts) > 1 else ""
                        dot_index = raw_value.find(".")
                        if dot_index != -1:
                            aircraft_code = raw_value[dot_index + 1 :].split()[0]
                        else:
                            aircraft_code = raw_value.split()[0]
                    elif lower_detail.startswith("weapons"):
                        weapon_code = detail.split()[-1]
                        if aircraft_code:
                            aircraft_entries.append(
                                MissionAircraft(
                                    aircraft_code=aircraft_code.strip(),
                                    weapon_code=weapon_code.strip(),
                                    skins=frozenset(skin_set),
                                )
                            )
                            logger.debug(
                                "Recorded aircraft %s with weapon %s and %d skins",
                                aircraft_code.strip(),
                                weapon_code.strip(),
                                len(skin_set),
                            )
                    idx += 1
                continue

        if lower_line == "[chiefs]":
            while idx < total_lines:
                entry = lines[idx].strip()
                if not entry:
                    idx += 1
                    continue
                if entry.startswith("["):
                    break

                fields = entry.split()
                if "ShipPack" in entry:
                    logger.warning("Possible ShipPack mismatch detected in line: %s", entry)
                if len(fields) > 1:
                    segment = fields[1]
                    chief = segment.split(".", 1)[-1]
                    chiefs_list.add(chief)
                    logger.debug("Registered chief %s", chief)
                idx += 1
            continue

        if lower_line == "[nstationary]":
            while idx < total_lines:
                entry = lines[idx].strip()
                if not entry:
                    idx += 1
                    continue
                if entry.startswith("["):
                    break

                fields = entry.split()
                if len(fields) > 1:
                    stationary_name = fields[1]
                    stationaries_list.add(stationary_name)
                    lower_stationary = stationary_name.lower()
                    if "vehicles.planes" in lower_stationary:
                        if (len(fields) >= 2 and fields[-1].lower() == "null") or (
                            len(fields) >= 3 and fields[-1] == "0" and fields[-2].lower() == "null"
                        ):
                            stat_planes_without_markings.append(stationary_name)
                            logger.debug(
                                "Stationary plane without markings found: %s",
                                stationary_name,
                            )
                idx += 1
            continue

        if lower_line == "[buildings]":
            while idx < total_lines:
                entry = lines[idx].strip()
                if not entry:
                    idx += 1
                    continue
                if entry.startswith("["):
                    break

                fields = entry.split()
                if len(fields) > 1:
                    buildings_list.append(fields[1])
                    logger.debug("Registered static object %s", fields[1])
                idx += 1
            continue

    mission_date = None
    if date_year is not None and date_month is not None and date_day is not None:
        mission_date = MissionDate(year=date_year, month=date_month, day=date_day)

    if not player_sqdn:
        logger.warning("Player squadron not found in %s", path.name)
    if map_name is None:
        logger.warning("Map not detected in %s", path.name)
    if mission_date is None:
        logger.warning("Date not fully specified in %s", path.name)

    logger.debug(
        "Mission summary for %s: aircraft=%d, chiefs=%d, stationaries=%d, buildings=%d, wings=%d",
        path.name,
        len(aircraft_entries),
        len(chiefs_list),
        len(stationaries_list),
        len(buildings_list),
        len(wing_sections),
    )

    return MissionData(
        path=path,
        map_name=map_name,
        date=mission_date,
        date_is_custom=date_is_custom,
        player_squadron=player_sqdn,
        aircraft=tuple(aircraft_entries),
        chiefs=frozenset(chiefs_list),
        stationaries=frozenset(stationaries_list),
        buildings=tuple(buildings_list),
        wing_sections=tuple(wing_sections),
        stat_planes_without_markings=tuple(stat_planes_without_markings),
    )
