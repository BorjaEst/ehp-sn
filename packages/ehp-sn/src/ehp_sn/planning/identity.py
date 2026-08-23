"""Generic identity-bearing input representation (Capability 6).

This module defines the small generic value a producer declares when it says
"these scientific inputs contribute to build identity." It is the framework's
*representation* of producer-declared identity inputs; it carries no meaning
attached to a field (the framework never interprets the names or values).

Ownership boundary (Capability-6 design note §5):

* the producer declares WHAT contributes to scientific identity;
* the framework binds/incorporates those declarations into the immutable plan
  and, in later capabilities, into build-input identity computation.

An :class:`IdentityInput` is a canonical (name, value) pair. The producer emits
them in a stable, deterministic order so that "same scientific inputs → same
identity representation" and "different identity-bearing input → different
representation" hold as plain structural equality of the immutable plan. No
hashing expectation is invented here: the current identity contract defines no
digest semantics, so Capability 6 only establishes the canonical, comparable
declaration form (``docs/invariants.md`` / Capability-6 design note §13).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class IdentityInput:
    """One canonical producer-declared identity-bearing scientific input.

    ``name`` is a stable producer-owned key (for example ``variant``,
    ``source_reference``); ``value`` is its effective semantic value. The
    framework does not interpret either; it only binds them in declaration
    order into the immutable plan.
    """

    name: str
    value: Any


__all__ = ["IdentityInput"]
