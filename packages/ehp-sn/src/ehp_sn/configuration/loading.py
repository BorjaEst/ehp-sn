"""Generic configuration loading (Capability 4).

This module is the framework-owned generic configuration input primitive. It
reads one concrete configuration source into a framework-owned configuration
document — a :class:`LoadedConfiguration` — using the authoritative physical
format for that source.

It deliberately:

* does **not** know component kinds, substrate families, or scientific
  configuration keys;
* does **not** interpret any producer-specific field;
* does **not** perform planning, semantic resolution, or validation of
  scientific content;
* does **not** compute configuration hashes, identities, or digests;
* does **not** implement composition (includes, inheritance, overrides,
  profiles, environment variables, ``--set``).

Its only responsibility is the deliberately boring pipeline::

    path
     ↓
    open / read
     ↓
    parse authoritative physical config format
     ↓
    generic loaded configuration document

The parsed values are preserved as returned by the parser, without sorting,
renaming, default injection, coercion, normalization, or dropping of unknown
keys. The ``source`` field is a diagnostic source location; it is not, by
itself, an identity-bearing input.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ConfigurationAccessError, ConfigurationParseError


@dataclass(frozen=True)
class LoadedConfiguration:
    """A generic configuration document parsed from one source.

    This object means only:

    * these values were parsed, and
    * they came from this configuration source.

    It does **not** mean the values are a valid concrete configuration, an
    effective configuration with scientific defaults, a build identity, or an
    execution-ready configuration. Scientific interpretation is owned
    downstream by research producers (Capability 5).

    ``source`` is the path the configuration was loaded from. It is a
    diagnostic / source location, not an identity-bearing input.
    """

    source: Path
    values: Mapping[str, Any]


def load_configuration(source: str | Path) -> LoadedConfiguration:
    """Load a configuration source into a generic loaded configuration document.

    Reads the file named by ``source`` and parses it in the authoritative
    physical configuration format. For the current repository profile format
    this is TOML; a ``.toml`` source is parsed with the standard TOML parser
    (``tomllib``).

    Raises:

    * :class:`ConfigurationAccessError` if ``source`` is missing, is not a
      regular readable file, or cannot be read.
    * :class:`ConfigurationParseError` if the content cannot be decoded or
      parsed as the configured format.
    """
    path = Path(source)

    try:
        raw = path.read_bytes()
    except OSError as exc:
        # A missing path, a directory, or a permission/IO failure all surface
        # here as an inaccessible source.
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
