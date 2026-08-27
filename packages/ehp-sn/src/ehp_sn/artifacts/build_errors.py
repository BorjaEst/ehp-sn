"""Controlled framework build errors for the corrected durable lifecycle.

This module owns the framework-domain error categories of the generic build and
publication boundary:

* :class:`BuildError` — a producer-specific (or otherwise unknown) build failure
  translated at the generic boundary;
* :class:`ConflictBuildError` — an immutable release coordinate is occupied by
  different content;
* :class:`InvalidExistingStateBuildError` — the destination contains
  incomplete/corrupt content;
* :class:`ReleaseNotConfiguredBuildError` — the build has no configured release
  coordinate (the framework never auto-assigns one).

These are framework-domain errors, not CLI categories; the CLI maps each to its
own exit-code category.
"""

from __future__ import annotations


class BuildError(Exception):
    """A controlled framework build failure at the generic public boundary.

    Raised when a substrate build cannot complete. It is a framework-domain
    error, not a CLI category; the CLI maps it at its own layer. The originating
    producer exception (if any) is preserved as the cause for diagnostics.
    """


class ConflictBuildError(BuildError):
    """A durable release coordinate is occupied by incompatible content."""


class InvalidExistingStateBuildError(BuildError):
    """The destination contains incomplete or corrupt content."""


class ReleaseNotConfiguredBuildError(BuildError):
    """No explicit release coordinate is configured for the build."""


__all__ = [
    "BuildError",
    "ConflictBuildError",
    "InvalidExistingStateBuildError",
    "ReleaseNotConfiguredBuildError",
]
