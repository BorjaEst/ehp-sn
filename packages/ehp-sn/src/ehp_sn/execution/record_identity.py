"""Generic framework record-identity mechanism (Capability 9).

This module establishes the framework-owned, deterministic mechanism by which a
logical record inside a framework data artifact receives its stable
:attr:`record_id` (``docs/docs/framework/contracts/index.md`` § "Per-record
identity and record envelope").

The ownership boundary the four substrate specifications collectively imply:

.. code-block:: text

    producer
        determines the family-specific semantic identity inputs
        (realization key)
                ↓
    framework
        applies the canonical framework identifier mechanism
        (derive_record_id)
                ↓
    record_id

The framework must not decide what scientifically identifies one family's
topology realization versus another's categorical realization — that semantic
material is producer-declared. Conversely the producer does not invent the
canonical ``record_id``: it supplies canonical realization identity inputs and
the framework derives the opaque, deterministic, storage-independent identifier.

:func:`derive_record_id` therefore:

* is **deterministic** — equal inputs yield equal identifiers;
* is **independent of storage, worker scheduling, and enumeration order** — the
  realization key carries only producer-declared identity, never an index the
  framework appends;
* is **not a content digest** — it cannot be computed from scientific payload
  content alone and does not collapse distinct realizations that happen to share
  content;
* is **independent of plan identity** — a plan-wide choice (for example a split
  count) must not change an existing realization's ``record_id``, so plan
  identity is deliberately excluded from the derivation.

The exact digest algorithm is owned by ``docs/docs/framework/digests.md``; this
mechanism applies it (via :func:`ehp_sn.digests.canonical_digest`) without
redefining it. The digest mechanism itself is framework-wide and shared with
planning and artifact fingerprinting; execution does not depend on a
planning-specific utility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ehp_sn.digests import canonical_digest
from ehp_sn.planning import IdentityInput


@dataclass(frozen=True, slots=True)
class RealizationKey:
    """Producer-declared canonical identity inputs for one intended record.

    These are the family-specific semantic inputs that identify *which intended
    scientific realization this is* (for example a variant, realization index,
    base seed, split, and record-local generation parameters). The framework
    never interprets them; it only canonicalizes them into the ``record_id``.

    ``inputs`` are canonical ``(name, value)`` identity pairs in a stable,
    deterministic producer order.
    """

    inputs: tuple[IdentityInput, ...]


def derive_record_id(
    component_canonical: str,
    record_schema: str,
    realization_key: RealizationKey,
) -> str:
    """Derive the framework-owned stable ``record_id`` for one logical record.

    ``component_canonical`` is the canonical reference of the producing
    component (for example ``substrate:some-family/v1``), ``record_schema`` is
    the output schema reference the record conforms to, and ``realization_key``
    is the producer-declared realization identity. The result is opaque,
    deterministic, and independent of plan identity and enumeration order.

    The derivation includes:

    .. code-block:: text

        framework_record_id(
            producer/component identity,
            record schema,
            realization key
        )
    """
    return canonical_digest(
        {
            "component": component_canonical,
            "schema": record_schema,
            "realization_key": [
                {"name": item.name, "value": item.value} for item in realization_key.inputs
            ],
        }
    )


def realization_key_value(realization_key: RealizationKey, name: str) -> Any:
    """Return the value of the identity input ``name`` within ``realization_key``.

    A small convenience for framework code that must read a producer-declared
    descriptor off a realization key without knowing the family semantics. The
    framework does not branch on the value; it only reads an explicitly named
    producer descriptor (for example a split label that the producer already
    declared as part of record identity). Raises :class:`KeyError` when absent.
    """
    for item in realization_key.inputs:
        if item.name == name:
            return item.value
    raise KeyError(name)


__all__ = ["RealizationKey", "derive_record_id", "realization_key_value"]
