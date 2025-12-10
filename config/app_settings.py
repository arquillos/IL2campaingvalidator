"""Application settings helpers."""

import logging

from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppSettings:
    """Structured representation of the campaign analyzer settings."""

    std_path: Path
    skin_path: Path
    campaign_path: Path
    output_directory: Path
    output_path: Path
    auto_correct_static_markings: bool
    auto_replace_stationary_objects: bool
    make_non_player_ai_only: bool
    report_format: bool

    def __str__(self) -> str:
        return f"\n\tSTD path: {self.std_path}" \
        f"\n\tSkins path:{self.skin_path}" \
        f"\n\tCampaign path: {self.campaign_path}" \
        "\n\tSwitches" \
        f"\n\t - Fix Static markings: {'Yes' if self.auto_correct_static_markings else 'No'}" \
        f"\n\t - Replace Stationary objects: {'Yes' if self.auto_replace_stationary_objects else 'No'}" \
        f"\n\t - [Coop] Non player flights AI only: {'Yes' if self.make_non_player_ai_only else 'No'}" \
        f"\n\t - Report format: {'Reduced' if self.report_format else 'Full'}" \
        f"\n\tReport: {self.output_path}"

def read_app_settings() -> AppSettings:
    """Read settings from the legacy INI-style text file."""

    settings_path = Path("settings.ini")
    logger.info("Loading application settings from %s", settings_path)

    config = ConfigParser(interpolation=None)
    def _identity(optionstr: str) -> str:
        return optionstr

    config.optionxform = _identity  # preserve original key casing

    with settings_path.open(encoding="utf-8") as handle:
        contents = handle.read()

    config.read_string("[settings]\n" + contents)
    section = config["settings"]

    def _path(option: str) -> Path:
        raw_value = section.get(option, fallback="").strip().strip('"')
        return Path(raw_value) if raw_value else Path()

    std_path = _path("STD_PATH_FOLDER")
    skin_path = _path("SKIN_PATH_FOLDER")
    campaign_path = _path("CAMPAIGN_PATH_FOLDER")
    output_directory = _path("OUTPUT_PATH_FOLDER")
    output_path = output_directory / "CampaignAnalyzerOutput.txt"

    def _flag(option: str) -> bool:
        return section.getint(option, fallback=0) != 0

    settings = AppSettings(
        std_path=std_path,
        skin_path=skin_path,
        campaign_path=campaign_path,
        output_directory=output_directory,
        output_path=output_path,
        auto_correct_static_markings=_flag("AUTO_CORRECT_STATIC_AIRCRAFT_MARKINGS"),
        auto_replace_stationary_objects=_flag("AUTO_REPLACE_STATIONARY_OBJECTS"),
        make_non_player_ai_only=_flag("NON_PLAYER_AI_ONLY"),
        report_format=_flag("REPORT_FORMAT")
    )

    logger.info(settings)

    return settings
