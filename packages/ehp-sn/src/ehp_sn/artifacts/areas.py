from __future__ import annotations

from enum import StrEnum
from pathlib import Path


class DataArea(StrEnum):
    EXTERNAL = "external"
    RAW = "raw"
    INTERIM = "interim"
    PROCESSED = "processed"


def data_area_path(data_root: Path, area: DataArea) -> Path:
    return data_root / area.value


__all__ = ["DataArea", "data_area_path"]
