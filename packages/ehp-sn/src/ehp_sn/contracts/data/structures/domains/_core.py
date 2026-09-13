from __future__ import annotations

from dataclasses import dataclass

ROLE = "domains"


class AmbientDomainError(ValueError):
    pass


@dataclass(frozen=True)
class Domain:
    """Internal family root for ambient-domain contracts.

    It deliberately declares no domain payload. What, if anything, every
    registered domain schema shares is decided by the domain-contract slice,
    once the rectangular and hexagonal declarations have actually been
    compared. A payload-free root also keeps the concrete declarations free to
    choose their own schema-specific shape parameters.
    """


__all__ = ["AmbientDomainError", "Domain", "ROLE"]
