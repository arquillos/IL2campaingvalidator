"""Utilities for scanning skin directories."""

import logging

from pathlib import Path


# TODO: Support more skin file types if needed (.jpg, .tga, etc.)
SKIN_SUFFIXES = {".bmp"}


logger = logging.getLogger(__name__)


def read_skins(root: Path) -> dict[str, list[str]]:
    """Return a mapping of skin folders (lowercased) to available skins."""

    logger.info("Scanning skins in %s", root)

    # Dictionary of skin folder (lowercase) to list of skin filenames
    skin_directory: dict[str, list[str]] = {}

    for subdir in root.iterdir():
        if not subdir.is_dir():
            continue

        entries = [file.name for file in subdir.iterdir() if file.suffix.lower() in SKIN_SUFFIXES]
        skin_directory[subdir.name.lower()] = sorted(entries)

    logger.debug("Collected skins for %d folders", len(skin_directory))
    return skin_directory
