"""Generic canonical component references.

The canonical reference grammar is owned by
``docs/docs/framework/references.md``:

    <kind>:<name>/v<N>

* ``kind`` identifies the component or resource category (``task``, ``model``,
  ``substrate``, ``binding``, ``experiment``, ``artifact``, ...);
* ``name`` is a unique identifier within the kind namespace and may contain
  internal path separators;
* ``v<N>`` is the specification version for component kinds.

A ``ComponentRef`` is the generic, kind-agnostic reference representation used
across the framework (``bindings`` already imports it from here). The substrate
portion of a reference is a component kind, not a separate reference system:
there is deliberately no ``SubstrateReference``-style subtype.

All reference kinds share the same parsing/canonicalization behavior. This
module holds no component-family-specific logic (ARCH-001/ARCH-003).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: Canonical component-reference grammar: ``<kind>:<name>/v<N>``.
#
# ``kind``: one or more of ASCII letters, digits, ``-``, ``_``.
# ``name``: one or more of ASCII letters, digits, ``-``, ``_``, ``.``, ``/``
#           (internal path separators are permitted by the specification).
# ``version``: lower-case ``v`` followed by one or more decimal digits.
_COMPONENT_REF_RE = re.compile(
    r"^(?P<kind>[A-Za-z0-9_-]+):"
    r"(?P<name>[A-Za-z0-9_.\-/]+)"
    r"/v(?P<version>[0-9]+)$"
)


class InvalidReferenceError(ValueError):
    """A text did not conform to a canonical component reference.

    Owned by the reference subsystem: reference syntax failures are reported
    here, at parse time, rather than by the discovery registry.
    """


@dataclass(frozen=True, slots=True)
class ComponentRef:
    """A canonical component reference.

    Immutable and value-equal. Fields:

    * ``kind`` — the component or resource category;
    * ``name`` — the identifier within the kind namespace;
    * ``version`` — the numeric component specification version.
    """

    kind: str
    name: str
    version: int

    def __post_init__(self) -> None:
        """Validate the declared fields form a canonical reference."""
        # Re-canonicalize to enforce one normalized form and reject any
        # malformed combination at construction time.
        canonical = f"{self.kind}:{self.name}/v{self.version}"
        match = _COMPONENT_REF_RE.match(canonical)
        if match is None:
            raise InvalidReferenceError(f"invalid canonical component reference: {canonical!r}")

    @property
    def canonical(self) -> str:
        """The canonical string form ``<kind>:<name>/v<N>``."""
        return f"{self.kind}:{self.name}/v{self.version}"

    def __str__(self) -> str:
        return self.canonical

    @classmethod
    def parse(cls, text: str) -> ComponentRef:
        """Parse a canonical component reference from ``text``.

        Raises :class:`InvalidReferenceError` when ``text`` is not a valid
        canonical component reference.
        """
        match = _COMPONENT_REF_RE.match(text)
        if match is None:
            raise InvalidReferenceError(f"invalid canonical component reference: {text!r}")
        return cls(
            kind=match.group("kind"),
            name=match.group("name"),
            version=int(match.group("version")),
        )
