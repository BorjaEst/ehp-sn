"""Registry-backed adapter that connects ``ehp-sn data`` to the framework registry.

This module adapts real framework objects (registered component definitions from
the generic :class:`ehp_sn.discovery.ComponentRegistry`) to the temporary
CLI-facing seam declared in ``cli/_data_service.py``.

The two responsibilities are deliberately separated:

* ``cli/_data_service.py`` — defines the CLI-facing seam: the ``DataService``
  protocol, the presentation result containers, and the stable user-facing error
  categories;
* ``cli/data_adapter.py`` — adapts real framework objects to that seam.

:class:`FrameworkDataService` is the *production* backend: ``list``/``show`` are
backed by the effective application registry, and ``plan``/``build``/``validate``/
``inspect`` remain explicitly unimplemented for this capability (they raise
:class:`DataNotImplementedError`, surfaced by the CLI as a controlled failure).
It intentionally holds no producer-specific branches or metadata maps; it
projects registered definitions directly.

The adapter consumes the effective application registry; it does not own or
construct one. It is structurally compatible with the ``DataService`` protocol;
explicit inheritance from a ``Protocol`` is not required.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, cast

from ehp_sn.discovery import ComponentRegistry
from ehp_sn.discovery.registry import UnknownReferenceError
from ehp_sn.experiments import ComponentRef, InvalidReferenceError

from ._data_service import (
    BuildResult,
    DataNotImplementedError,
    InspectResult,
    ListedSubstrate,
    PlanResult,
    ShowResult,
    UnknownSubstrateError,
    ValidateResult,
)

#: The component kind this adapter's operations accept.
_SUBSTRATE_KIND = "substrate"


class _RegisteredSubstrate(Protocol):
    """Structural shape of a registered substrate definition the adapter projects.

    The generic discovery contract (``DiscoverableDefinition``) exposes only
    ``ref`` and ``kind``. For ``list``/``show`` a substrate definition must also
    carry its authoritative description and normalized output contract. The
    adapter reads those structurally from the exact registered object (the
    registry preserves identity); it does not maintain a parallel metadata map.
    """

    ref: ComponentRef
    kind: str
    description: str
    output_contract: str


def _project_listed_substrate(definition: _RegisteredSubstrate) -> ListedSubstrate:
    """Project a registered substrate definition into a ``data list`` row."""
    return ListedSubstrate(
        ref=definition.ref.canonical,
        family=definition.ref.name,
        output=definition.output_contract,
    )


def _project_show_result(definition: _RegisteredSubstrate) -> ShowResult:
    """Project a registered substrate definition into a ``data show`` result."""
    return ShowResult(
        ref=definition.ref.canonical,
        description=definition.description,
    )


class FrameworkDataService:
    """The registry-backed production backend for the ``ehp-sn data`` CLI group.

    ``list`` enumerates registered substrate definitions from the injected
    registry; ``show`` resolves one authoritative definition and projects it.
    The remaining lifecycle operations are explicitly not implemented yet.
    """

    def __init__(self, registry: ComponentRegistry) -> None:
        self._registry = registry

    def _resolve_substrate(self, target: str) -> _RegisteredSubstrate:
        """Resolve ``target`` and ensure it denotes a substrate.

        Translates generic framework failures (unknown reference, malformed
        reference) into the CLI-facing :class:`UnknownSubstrateError`, and
        enforces the CLI's operation-specific constraint that the target denote
        a substrate — a generic registry capability, not a new discovery
        primitive. The generic registry never raises a CLI category.
        """
        try:
            definition = self._registry.resolve(target)
        except (UnknownReferenceError, InvalidReferenceError) as exc:
            raise UnknownSubstrateError(f"unknown substrate: {target}") from exc
        if definition.kind != _SUBSTRATE_KIND:
            raise UnknownSubstrateError(f"reference {target} does not denote a substrate")
        return cast("_RegisteredSubstrate", definition)

    def list(self) -> Sequence[ListedSubstrate]:
        """List the registered substrate definitions, in discovery order."""
        definitions = self._registry.iter(kind=_SUBSTRATE_KIND)
        return tuple(
            _project_listed_substrate(cast("_RegisteredSubstrate", definition))
            for definition in definitions
        )

    def show(self, target: str) -> ShowResult:
        """Describe one registered substrate definition, resolved via the registry."""
        definition = self._resolve_substrate(target)
        return _project_show_result(definition)

    def plan(self, target: str, config: str | None) -> PlanResult:
        raise DataNotImplementedError(
            f"data plan is not yet implemented by the framework backend (target: {target})."
        )

    def build(self, target: str, config: str | None) -> BuildResult:
        raise DataNotImplementedError(
            f"data build is not yet implemented by the framework backend (target: {target})."
        )

    def validate(self, artifact: str, level: str) -> ValidateResult:
        raise DataNotImplementedError(
            f"data validate is not yet implemented by the framework backend (artifact: {artifact})."
        )

    def inspect(self, artifact: str, samples: int) -> InspectResult:
        raise DataNotImplementedError(
            f"data inspect is not yet implemented by the framework backend (artifact: {artifact})."
        )
