"""Generic framework configuration loading.

This package owns the framework configuration *mechanics* (Capability 4): a
generic loader that reads one concrete configuration source into a framework-
owned generic configuration document, without interpreting any scientific or
producer-specific field.

Semantic configuration resolution is owned downstream by research producers
(Capability 5) and is deliberately not implemented here.

Public surface is exposed from the owning submodules:

* :func:`load_configuration` and :class:`LoadedConfiguration` from
  :mod:`ehp_sn.configuration.loading`;
* the generic error taxonomy from :mod:`ehp_sn.configuration.errors`.
"""

from __future__ import annotations

from .errors import (
    ConfigurationAccessError,
    ConfigurationError,
    ConfigurationParseError,
)
from .loading import LoadedConfiguration, load_configuration

__all__ = [
    "ConfigurationAccessError",
    "ConfigurationError",
    "ConfigurationParseError",
    "LoadedConfiguration",
    "load_configuration",
]
