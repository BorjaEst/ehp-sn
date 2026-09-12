from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ConfigurationAccessError, ConfigurationParseError


@dataclass(frozen=True)
class LoadedConfiguration:
    source: Path
    values: Mapping[str, Any]


def load_configuration(source: str | Path) -> LoadedConfiguration:
    path = Path(source)

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ConfigurationAccessError(f"cannot read configuration source {str(path)!r}: {exc}") from exc

    try:
        values = tomllib.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ConfigurationParseError(
            f"configuration source {str(path)!r} is not valid UTF-8: {exc}"
        ) from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigurationParseError(
            f"configuration source {str(path)!r} is not valid TOML: {exc}"
        ) from exc

    return LoadedConfiguration(source=path, values=values)
