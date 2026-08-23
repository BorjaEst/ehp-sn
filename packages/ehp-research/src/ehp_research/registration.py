"""Explicit provider integration point for research component definitions.

This module is a *package integration point*, not a catalogue. Its only
responsibility is to register authoritative research definition objects into a
generic ``ehp_sn`` registry (the Capability-1 discovery mechanism):

.. code-block:: text

    authoritative definition objects
                ↓
    generic ehp_sn registry

The provider manifest (``_COMPONENTS``) lists which definitions this package
exposes in this phase — nothing more. It never redefines what a definition
means and never duplicates a definition's metadata; the scientific facts live
with each family's authoritative definition object (its ``ref``, description,
and output contract).

Registration is explicit and side-effect free: importing ``ehp_research`` does
not mutate any registry. Population happens only when a consumer calls
:func:`register_components` with an explicit registry instance. Duplicate
handling and duplicate detection are owned by the generic registry itself;
this function deliberately does not re-implement them.

See ``docs/invariants.md`` ARCH-001/ARCH-003 and the package README's
"Registration and discovery" section.
"""

from __future__ import annotations

from ehp_sn.discovery import ComponentRegistry

from .substrates.dagflow import DAGFLOW_DEFINITION
from .substrates.maze_nd import MAZE_ND_DEFINITION

#: Provider manifest for this capability: the authoritative Dagflow and Maze-ND
#: definitions. DungeonGen and ObsField are intentionally not registered yet
#: (phase control: they serve as later generality tests).
_COMPONENTS = (
    DAGFLOW_DEFINITION,
    MAZE_ND_DEFINITION,
)


def register_components(registry: ComponentRegistry) -> None:
    """Register the research definitions exposed by this package into ``registry``.

    The operation is explicit: definitions are registered into the caller's
    registry, never into an implicit global. It performs no duplicate detection
    of its own — the generic registry remains the authority, so registering the
    same canonical reference twice raises the generic
    :class:`DuplicateRegistrationError` (``ehp_sn.discovery``).
    """
    for definition in _COMPONENTS:
        registry.register(definition)


__all__ = ["register_components"]
