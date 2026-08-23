"""Generic framework configuration errors.

These are framework-owned generic configuration errors for the configuration
*loading* layer (Capability 4). They distinguish an inaccessible source from
content that cannot be parsed as the configured format. They carry no
substrate or producer semantics and no CLI exit-code classification; the CLI
boundary translates them at its own layer (``ehp_sn.cli``).

Error taxonomy:

* :class:`ConfigurationAccessError` — the configuration source cannot be read:
  the path does not exist, names a non-file object, or a relevant I/O failure
  prevents access.
* :class:`ConfigurationParseError` — the configuration source is accessible
  but its content cannot be parsed in the configured format.

These do **not** cover producer-specific semantic validation. Semantic
interpretation of loaded values is owned by downstream research producers
(Capability 5) and is deliberately out of scope here.
"""

from __future__ import annotations


class ConfigurationError(Exception):
    """Base class for generic framework configuration errors."""


class ConfigurationAccessError(ConfigurationError):
    """The configuration source is missing, non-file, or otherwise unreadable.

    Raised when the source cannot be opened or read — for example, the path
    does not exist, it names a directory or other unsuitable filesystem
    object, or a relevant I/O failure prevents access.
    """


class ConfigurationParseError(ConfigurationError):
    """The configuration content cannot be parsed in the configured format.

    Raised when the source is accessible but decoding or parsing fails — for
    example, a ``.toml`` source that is not syntactically valid TOML.
    """
