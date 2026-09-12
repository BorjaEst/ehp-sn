from __future__ import annotations


class ConfigurationError(Exception): ...


class ConfigurationAccessError(ConfigurationError): ...


class ConfigurationParseError(ConfigurationError): ...
