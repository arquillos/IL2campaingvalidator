"""Common helpers for loading text-based resources."""

import logging

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TextIO, TypeVar


T = TypeVar("T")

logger = logging.getLogger(__name__)


def load_resource(
    root: str | Path,
    relative_path: Iterable[str],
    parser: Callable[[TextIO], T],
    resource_label: str,
) -> T:
    """Open a resource file and delegate parsing to ``parser``.

    The helper centralises logging, path resolution, and error handling for
    resource readers that all follow the same pattern.
    """

    resource_path = Path(root, *relative_path)
    logger.info("Loading %s from %s", resource_label, resource_path)

    try:
        try:
            with resource_path.open(encoding="utf-8") as handle:
                result = parser(handle)
        except UnicodeDecodeError:
            logger.warning(
                "Failed to decode %s as UTF-8; retrying with Windows-1251 encoding",
                resource_path,
            )
            with resource_path.open(encoding="cp1251") as handle:
                result = parser(handle)
    except FileNotFoundError:
        logger.exception("%s not found at %s", resource_label, resource_path)
        raise

    _log_result_size(result, resource_label)
    return result


def _log_result_size(result: object, resource_label: str) -> None:
    if hasattr(result, "__len__"):
        try:
            count = len(result)  # type: ignore[arg-type]
        except TypeError:
            return
        logger.debug("Loaded %d %s entries", count, resource_label)
