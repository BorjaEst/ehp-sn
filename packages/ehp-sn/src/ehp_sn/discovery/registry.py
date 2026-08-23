"""Generic framework component registry.

A ``ComponentRegistry`` is the single generic, deterministic registration and
resolution authority for framework component definitions. It stores arbitrary
definitions keyed by their canonical ``ComponentRef``, enumerates them by
component kind, and resolves the original authoritative definition object.

Capability boundary (``docs/invariants.md`` ARCH-003):

* registration uses canonical component references;
* catalogue semantics do not depend on registration order;
* conflicting duplicate canonical references are rejected.

This module contains no scientific semantics. It never imports ``ehp_research``
and never branches on a component family or kind beyond treating ``kind`` as an
opaque grouping key.

No provider abstraction, plugin architecture, or package-loading mechanism
lives here: how installed definitions populate an application registry is a
separate capability. The primitive capability is ``register(definition)``.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..experiments.refs import ComponentRef

# ---------------------------------------------------------------------------
# Framework-level failures
#
# These are framework errors, not CLI errors. The CLI maps them to its own
# user-facing categories and exit codes in a later capability; process
# semantics stay out of the framework domain.
# ---------------------------------------------------------------------------


class RegistryError(Exception):
    """Base class for controlled framework registry failures."""


class DuplicateRegistrationError(RegistryError):
    """A definition was registered under an already-registered canonical reference.

    The first registered definition remains authoritative; the second must not
    silently replace it.
    """


class UnknownReferenceError(RegistryError):
    """A canonical reference does not match any registered definition."""


# ---------------------------------------------------------------------------
# Discovery contract
#
# "discovery contract" answers one question: what object is this?
# It intentionally carries no producer behavior (no description, schema,
# builder, validity, planner, or resource requirements). Those belong to a
# concrete definition contract, not to generic discovery.
# ---------------------------------------------------------------------------


@runtime_checkable
class DiscoverableDefinition(Protocol):
    """A registered component definition.

    Generic discovery requires only:

    * ``ref`` — the definition's canonical component reference;
    * ``kind`` — the component kind (which must match ``ref.kind``).

    The registry stores the definition object itself and never copies or wraps
    its metadata, so resolution returns the same authoritative object.
    """

    @property
    def ref(self) -> ComponentRef: ...

    @property
    def kind(self) -> str: ...


# ---------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Entry:
    """Internal immutable registry entry.

    Bundles a registered definition with its canonical key and kind so both
    deterministic enumeration and identity-preserving resolution are cheap.
    """

    kind: str
    canonical: str
    definition: DiscoverableDefinition


class ComponentRegistry:
    """Store, enumerate, and resolve generic component definitions.

    The registry is keyed by canonical component reference. It does not import
    any provider package, does not interpret substrate/task/model semantics,
    and never modifies a registered definition.
    """

    __slots__ = ("_by_canonical",)

    def __init__(self) -> None:
        # Ordered mapping from canonical reference string -> _Entry. Using an
        # insertion-ordered dict keeps ``iter`` deterministic independent of
        # registration order once we sort by canonical reference.
        self._by_canonical: dict[str, _Entry] = {}

    def register(self, definition: DiscoverableDefinition) -> None:
        """Register ``definition`` under its canonical component reference.

        The definition is stored as-is (identity preserved); it is not copied.
        A duplicate canonical reference raises :class:`DuplicateRegistrationError`
        and leaves the first definition authoritative.
        """
        ref = definition.ref
        kind = definition.kind

        # A definition's declared kind must agree with the kind of its
        # canonical reference. This is a generic consistency invariant, not a
        # substrate-family rule.
        if kind != ref.kind:
            raise RegistryError(
                f"definition kind {kind!r} does not match its canonical "
                f"reference kind {ref.kind!r}: {ref.canonical!r}"
            )

        canonical = ref.canonical
        if canonical in self._by_canonical:
            raise DuplicateRegistrationError(
                f"a definition is already registered for canonical reference {canonical!r}"
            )
        self._by_canonical[canonical] = _Entry(kind=kind, canonical=canonical, definition=definition)

    def resolve(self, reference: str | ComponentRef) -> DiscoverableDefinition:
        """Return the registered definition for ``reference``.

        ``reference`` may be a canonical string or a :class:`ComponentRef`.
        Returns the exact registered object (identity preserved).

        Raises :class:`InvalidReferenceError` for malformed references (owned by
        the reference subsystem) and :class:`UnknownReferenceError` when the
        reference is not registered.
        """
        ref = reference if isinstance(reference, ComponentRef) else ComponentRef.parse(reference)
        try:
            return self._by_canonical[ref.canonical].definition
        except KeyError as exc:
            raise UnknownReferenceError(
                f"no definition registered for canonical reference {ref.canonical!r}"
            ) from exc

    def contains(self, reference: str | ComponentRef) -> bool:
        """Whether ``reference`` has a registered definition.

        Returns ``False`` for malformed references rather than raising.
        """
        if isinstance(reference, ComponentRef):
            return reference.canonical in self._by_canonical
        try:
            parsed = ComponentRef.parse(reference)
        except ValueError:
            return False
        return parsed.canonical in self._by_canonical

    def iter(self, *, kind: str | None = None) -> Iterable[DiscoverableDefinition]:
        """Iterate registered definitions in deterministic canonical order.

        When ``kind`` is given, only definitions of that component kind are
        yielded. Ordering is by canonical reference string, so catalogue
        semantics never depend on registration order.
        """
        entries = sorted(self._by_canonical.values(), key=lambda entry: entry.canonical)
        if kind is None:
            return (entry.definition for entry in entries)
        return (entry.definition for entry in entries if entry.kind == kind)
