""" Utils for logging the report """
from typing import Tuple

from missions.mission_data import MissionAircraft


def log_used_aircrafts(aircrafts: list[str], full_report: bool) -> None:
    """ Log the aircrafts used in a mission """
    used_aircraft = sorted({entry.aircraft_code for entry in aircrafts})

    if full_report:
        if used_aircraft:
            print("Aircraft used:\n" + "\n".join(f"\t{code}" for code in used_aircraft))
        else:
            print("Aircraft used:\n\tNone")

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
) -> None:
    """ Log the details for the aircrafts in a mission """
    for aircraft in aircrafts:
        aircraft_code = aircraft.aircraft_code
        aircraft_name = aircraft_classes.get(aircraft_code)
        if aircraft_name is None:
            print(f"###Aircraft {aircraft_code} not found!")
            continue

        skin_key = aircraft_name.lower()
        available_skins = skins.get(skin_key)
        for skin in sorted(aircraft.skins):
            if not available_skins or skin not in available_skins:
                print(f"###Skin {skin} for {aircraft_code} not found!")

        weapon_options = weapons.get(aircraft_name)
        if weapon_options is None or aircraft.weapon_code not in weapon_options:
            print(f"###Weapon {aircrafts.weapon_code} for {aircraft_code} not found!")


def log_planes_without_markings(stat_planes_without_markings: list[str]) -> None:
    """ Log the planes without markings in a mission """
    stat_planes_without_markings = sorted(set(stat_planes_without_markings))
    if stat_planes_without_markings:
        print("###These stationary planes have no markings:")
        for stat_plane_name in stat_planes_without_markings:
            print(f"\t{stat_plane_name}")


def log_buildings(buildings: list[str], objects: list[str]) -> None:
    """ Log the missing buildings in a mission """
    missing_buildings = set()

    for building in sorted(buildings):
        if building not in objects:
            missing_buildings.add(building)

    for building in sorted(list(missing_buildings)):
        print(f"###Missing static object {building}")
