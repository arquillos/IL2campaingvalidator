""" Utils for logging the report """

import logging 

from pathlib import Path
from typing import Tuple

from missions.mission_data import MissionAircraft

logger = logging.getLogger(__name__)


def log_used_aircrafts(aircrafts: list[str], full_report: bool) -> None:
    """ Log the aircrafts used in a mission """
    used_aircraft = sorted({entry.aircraft_code for entry in aircrafts})

    if full_report:
        if used_aircraft:
            print("Aircraft used:\n" + "\n".join(f"\t{code}" for code in used_aircraft))
        else:
            print("Aircraft used:\n\tNone")


def log_squadrons(wing_sections: list[str], full_report: bool) -> None:
    """ Log the Wings used in a mission """
    sorted_wings = sorted({entry for entry in wing_sections})

    if full_report:
        if sorted_wings:
            print("Wings:\n" + "\n".join(f"\t{wing}" for wing in sorted_wings))
        else:
            print("Wings used:\n\tNone")


def log_chiefs(chiefs: list[str], full_report: bool) -> None:
    """ Log the defined chiefs in a mission """
    sorted_chiefs = sorted(chiefs)

    if full_report:
        if sorted_chiefs:
            print("Chiefs used:\n" + "\n".join(f"\t{chief}" for chief in sorted_chiefs))
        else:
            print("Chiefs used:\n\tNone")

    for chief in sorted_chiefs:
        if chief not in chiefs:
            print(f"###Chief {chief} not found!")


def log_stationaries(stationaries: list[str], full_report: bool) -> None:
    """ Log the defined stationaries in a mission """
    sorted_stationaries = sorted(stationaries)

    if full_report:
        if sorted_stationaries:
            print(
                "Stationaries used: \n" + "\n".join(f"\t{item}" for item in sorted_stationaries)
            )
        else:
            print("Stationaries used: \n\tNone")

    for stationary in sorted_stationaries:
        if stationary not in stationaries:
            print(f"###Stationary {stationary} not found!")


def log_planes_details(
    aircrafts: Tuple[MissionAircraft, ...],
    aircraft_classes: list[str],
    skins: dict[str, list[str]],
    weapons: dict[str, list[str]],
) -> set[str]:
    """ Log the details for the aircrafts in a mission """
    missing_aircrafts: set[str] = set()

    print("### Aircrafts - Not found:")
    for aircraft in aircrafts:
        aircraft_code = aircraft.aircraft_code
        aircraft_name = aircraft_classes.get(aircraft_code)
        if aircraft_name is None:
            print(f"\t{aircraft_code}")
            missing_aircrafts.add(aircraft_name)
            continue

        skin_key = aircraft_name.lower()
        available_skins = skins.get(skin_key)
        print("### Skins - Missing:")
        for skin in sorted(aircraft.skins):
            if not available_skins or skin not in available_skins:
                print(f"\t{skin} for {aircraft_code}")

        weapon_options = weapons.get(aircraft_name)
        if weapon_options is None or aircraft.weapon_code not in weapon_options:
            print(f"\t - {aircraft_code}: Weapon {aircraft.weapon_code} not found")

    return missing_aircrafts


def log_planes_without_markings(stat_planes_without_markings: list[str]) -> None:
    """ Log the planes without markings in a mission """
    stat_planes_without_markings = sorted(set(stat_planes_without_markings))
    if stat_planes_without_markings:
        print("### Stationary planes without markings:")
        for stat_plane_name in stat_planes_without_markings:
            print(f"\t{stat_plane_name}")


def log_buildings(buildings: list[str], objects: list[str]) -> set[str]:
    """ Log the missing buildings in a mission """
    missing_buildings = set()


    for building in sorted(buildings):
        if building not in objects:
            missing_buildings.add(building)

    print("### Static objects - Not found")
    for building in sorted(list(missing_buildings)):
        print(f"\t{building}")

    # TODO: Improve the method
    return set(sorted(list(missing_buildings)))


def generate_missing_objects_ini(
        missing_objects: set[str],
        output_directory: Path
) -> None:
    """
    Generate an ini file with the missing static objects.
    The file will have the valid format to be added at the end of static.ini

    The objects will be searched in the static.ini file stored in the base directory.
    """
    logging.debug("Generating 'ini' files with missing buildings")

    # Output path can be made configurable in the future
    base_ini_path = Path("base/static.ini")
    output_path = output_directory / "_add_to_static.ini"

    if not base_ini_path.exists():
        logging.error("Base static.ini not found at %s", base_ini_path)
        return

    # Read entire base/static.ini and build a map of section name -> section text
    # Sections are of the form [section.name] and continue until the next section header
    sections: dict[str, list[str]] = {}
    current_section_name: str | None = None
    current_section_lines: list[str] = []

    with base_ini_path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]") and len(stripped) > 2:
                # Commit previous section if present
                if current_section_name is not None:
                    sections[current_section_name] = current_section_lines[:]

                # Start new section
                current_section_name = stripped[1:-1]
                current_section_lines = [line]  # include header line with original formatting
            else:
                # Accumulate lines for the current section (and preamble comments too if any)
                if current_section_name is not None:
                    current_section_lines.append(line)
                else:
                    # Lines before the first section are ignored for lookup
                    pass

        # Commit the last section if file ended during a section
        if current_section_name is not None:
            sections[current_section_name] = current_section_lines[:]

    # Normalize requested object names: they may come either as full section keys
    # (e.g., buildings.House$Wickerchair) or already bracketed. We'll strip brackets if present.
    def normalize(name: str) -> str:
        n = name.strip()
        if n.startswith("[") and n.endswith("]"):
            n = n[1:-1]
        return n

    normalized_missing = [normalize(x) for x in sorted(missing_objects)]

    # Write output file with the corresponding sections
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as out:
        out.write("// Auto-generated sections to append to static.ini\n")
        out.write("// Generated by campaign validator\n\n")

        wrote_any = False
        for key in normalized_missing:
            section = sections.get("buildings." + key)
            if section is None:
                print(f"###Static object section not found: [{key}]")
                continue
            # Ensure separation between sections
            if wrote_any:
                out.write("\n")
            out.writelines(section)
            wrote_any = True

    if wrote_any:
        print(f"Missing static objects written to {output_path}")
    else:
        print("### No matching sections found to write.")


def _convert_wing_to_reg(wing: str) -> str:
    """
    Convert the wing value to regInfo.propertie format
    Examples:
     - Wing: CA_NN01 -> CA_NN
     - Wing: CA_NN10 -> CA_NN
     - Wing: III_KG7603 -> III_KG76
     - Wing: I_SAGr12500 -> I_SAGr125
    """
    if len(wing) < 5:
        return wing

    return wing[0:-2]


def log_missing_squadrons(wing_sections: list[str], squadrons: list[str]) -> None:
    """ Log the missing Wings """
    missing_wings = set()

    for wing in wing_sections:
        squadron = _convert_wing_to_reg(wing)
        if squadron not in squadrons:
            missing_wings.add(squadron)


    if missing_wings:
        print("### Wings - Not configured")
        for wing in missing_wings:
            print(f"Wing: {wing}")
