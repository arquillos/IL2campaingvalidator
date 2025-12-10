"""Campaign Analyzer for IL-2 Sturmovik 1946."""

import logging

from contextlib import redirect_stdout
from pathlib import Path
import sys

from aircraft.aircraft import read_aircraft_classes
from chiefs.chiefs import read_chiefs
from config.app_settings import read_app_settings, AppSettings
from conversions.static_conversions import read_conversion_file
from missions.missions import read_mission, read_missions
from objects.objects import read_objects
from report.report import (
    log_buildings,
    log_chiefs,
    log_planes_details,
    log_planes_without_markings,
    log_stationaries,
    log_used_aircrafts
)
from skins.skins import read_skins
from stationary.stationary import read_stationaries
from weapons.weapons import read_weapons

logger = logging.getLogger(__name__)


def main(cli_arguments: AppSettings | None = None) -> None:
    """Validate missions for missing assets."""

    logger.info("Campaign analyzer started")

    if cli_arguments is not None:
        logger.debug("Using CLI-provided application settings")
        app_config = cli_arguments
    else:
        logger.debug("Loading application settings from configuration file")
        app_config = read_app_settings()

    app_config.output_directory.mkdir(parents=True, exist_ok=True)
    logger.debug("Output directory prepared at %s", app_config.output_directory)

    logger.info("Loading standard installation resources")
    aircraft_classes = read_aircraft_classes(app_config.std_path)
    chiefs = read_chiefs(app_config.std_path)
    skins = read_skins(app_config.skin_path)
    stationaries = read_stationaries(app_config.std_path)
    objects = read_objects(app_config.std_path)
    weapons = read_weapons(app_config.std_path)
    logger.info(
        "Resource counts | aircraft=%d chiefs=%d stationaries=%d objects=%d weapons=%d",
        len(aircraft_classes),
        len(chiefs),
        len(stationaries),
        len(objects),
        len(weapons),
    )

    mission_list = read_missions(app_config.campaign_path)
    logger.info("Discovered %d missions to analyze", len(mission_list))

    with app_config.output_path.open("w", encoding="utf-8") as output_stream:
        with redirect_stdout(output_stream):
            for mission_path in mission_list:
                mission_name = mission_path.name
                logger.info("Analyzing mission %s", mission_name)
                mission_data = read_mission(mission_path)
                print(f"Reading mission {mission_name}")

                if mission_data.map_name:
                    print(f"Mission Map = {mission_data.map_name}")

                if mission_data.date and mission_data.date_is_custom:
                    mission_date = mission_data.date
                    print(
                        f"Mission Date: {mission_date.year}-{mission_date.month}-{mission_date.day}"
                    )
                else:
                    print("###Mission Date not set")

                log_used_aircrafts(mission_data.aircraft, app_config.report_format)
                log_chiefs(mission_data.chiefs, app_config.report_format)
                log_stationaries(mission_data.stationaries, app_config.report_format)
                log_planes_details(
                    mission_data.aircraft, aircraft_classes, skins, weapons
                )
                log_planes_without_markings(mission_data.stat_planes_without_markings)
                log_buildings(mission_data.buildings, objects)

                # Auto-Fixes
                player_squadron = mission_data.player_squadron
                wing_list = list(mission_data.wing_sections)
                if app_config.auto_correct_static_markings or \
                    app_config.auto_replace_stationary_objects or \
                    app_config.make_non_player_ai_only:
                    output_mission_path = app_config.output_directory / mission_name
                    if not output_mission_path.exists():
                        logger.debug("Applying auto-fixes for mission %s", mission_name)
                        with mission_path.open(encoding="utf-8") as mission_file, output_mission_path.open(
                            "x", encoding="utf-8"
                        ) as mission_copy:
                            current_squadron = ""
                            for line in mission_file:
                                if app_config.make_non_player_ai_only:
                                    if line.lower().rstrip() == "[wing]":
                                        mission_copy.write(line)
                                        line = mission_file.readline()
                                        while line and not line.strip().startswith("["):
                                            identifier = line.strip()
                                            if identifier and identifier not in wing_list:
                                                wing_list.append(identifier)
                                                logger.debug(
                                                    "Mission %s auto-fix registered wing %s",
                                                    mission_name,
                                                    identifier,
                                                )
                                            mission_copy.write(line)
                                            line = mission_file.readline()
                                        if not line:
                                            break
                                    if line.strip().startswith("[") and line.strip()[1:-1] in wing_list:
                                        current_squadron = line.strip()[1:-1]
                                        if current_squadron != player_squadron:
                                            mission_copy.write(line)
                                            line = mission_file.readline()
                                            if not line:
                                                break
                                            mission_copy.write(line)
                                            line = mission_file.readline()
                                            if not line:
                                                break
                                            if "OnlyAI" not in line:
                                                mission_copy.write("  OnlyAI 1\n")
                                                logger.debug(
                                                    "Mission %s auto-fix set OnlyAI=1 for %s",
                                                    mission_name,
                                                    current_squadron,
                                                )
                                            else:
                                                mission_copy.write(line)
                                                line = mission_file.readline()
                                            if not line:
                                                break

                                if app_config.auto_replace_stationary_objects:
                                    dir_path = Path(__file__).resolve().parent
                                    logger.debug("Loading conversion database from %s", dir_path)
                                    conversion_db = read_conversion_file(dir_path)

                                    for item, replacement in conversion_db.items():
                                        if f"{item} " in line:
                                            line = line.replace(item, replacement)
                                            logger.debug(
                                                "Mission %s auto-fix replaced %s with %s",
                                                mission_name,
                                                item,
                                                replacement,
                                            )

                                if app_config.auto_correct_static_markings and "vehicles.planes" in line:
                                    line_data = line.split()
                                    if len(line_data) >= 2:
                                        if line_data[-1] == "0" and line_data[-2].lower() == "null":
                                            new_line = line.rstrip()[:-1] + "1"
                                            line = new_line + "\n"
                                            logger.debug(
                                                "Mission %s auto-fix corrected markings for %s",
                                                mission_name,
                                                line_data[1],
                                            )
                                        elif line_data[-1].lower() == "null":
                                            line = line.rstrip() + " 1\n"
                                            logger.debug(
                                                "Mission %s auto-fix appended markings for %s",
                                                mission_name,
                                                line_data[1],
                                            )

                                mission_copy.write(line)
                    else:
                        logger.debug(
                            "Skipped auto-fixes for %s, output already exists at %s",
                            mission_name,
                            output_mission_path,
                        )
                else:
                    logger.debug("Auto-fixes disabled for mission %s", mission_name)

                print()
                logger.info("Finished mission %s", mission_name)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    main()
