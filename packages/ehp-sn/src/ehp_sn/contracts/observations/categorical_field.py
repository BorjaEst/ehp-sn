"""Shared categorical observation field contract (``categorical-field/v1``).

This module is the ``ehp_sn``-owned implementation of the framework contract
specified by ``docs/docs/framework/contracts/observations/categorical-field-v1.md``.

It defines a producer-agnostic, consumer-agnostic logical record schema for a
persistent categorical observation assignment over an ambient spatial domain:
one categorical observation for every canonical position in the domain.

The contract owns:

* the categorical-field object: an ambient domain (reusing
  ``ambient-domain/v1``) plus a total categorical observation assignment over it
  (``CF-REC-001``);
* observation vocabulary identity and the anonymous/external vocabulary contract
  (``CF-REC-004``/``CF-REC-005``);
* position-order consistency (``CF-REC-002``), coverage conformance
  (``CF-REC-003``), and no topology dependency (``CF-REC-006``).

It deliberately does **not** know anything about a producing family, generation
seed, assignment protocol, topology, passability, or split. Categorical-field
records are independent of topology substrates (``categorical-field/v1`` §
"Scope and boundary").

### Vocabulary identity (executable-profile closure)

For the first executable rectangular profile, this contract supports the
**anonymous** vocabulary form whose immutable identity is established directly
from the resolved declared vocabulary identity (for example
``vocabulary.identity`` in the resolved configuration). No vocabulary registry is
invented; external-vocabulary resolution to an immutable identity is deferred
until demonstrated. Vocabulary compatibility is never inferred from cardinality
alone.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from ..domains import RectangularRowColumnDomain

#: The canonical logical record schema reference.
SCHEMA_REF: Final = "categorical-field/v1"

#: Fixed schema semantics of this contract (not negotiated variation).
VALUE_KIND: Final = "categorical"
COVERAGE: Final = "total"
PERSISTENT: Final = True


class CategoricalFieldError(ValueError):
    """A supplied field does not conform to ``categorical-field/v1``.

    Raised when the vocabulary or the observation assignment violates a
    contract invariant. It is a contract-domain error; producers translate it.
    """


@dataclass(frozen=True, slots=True)
class AnonymousVocabulary:
    """An anonymous observation vocabulary (``kind: anonymous``).

    ``identity`` is the immutable vocabulary identity (established directly from
    the resolved declared identity for the first executable profile; no registry
    is implied). ``cardinality`` is ``K >= 1``; the canonical observation-ID
    domain is ``{0, ..., K - 1}``.
    """

    identity: str
    cardinality: int

    @property
    def kind(self) -> str:
        """The vocabulary logical form."""
        return "anonymous"

    def declaration(self) -> dict[str, object]:
        """Return the canonical vocabulary declaration."""
        return {"kind": "anonymous", "identity": self.identity, "cardinality": self.cardinality}


@dataclass(frozen=True, slots=True)
class ExternalVocabulary:
    """An external observation vocabulary (``kind: external``).

    ``ref`` is the immutable external vocabulary reference; ``identity`` is the
    resolved immutable vocabulary identity; ``cardinality`` is ``K >= 1``.
    Resolution semantics are deferred to the reference mechanism / referenced
    vocabulary specification; this contract requires only that the resolved
    identity and cardinality are immutable and that assigned observation IDs
    resolve within the declared local domain.
    """

    ref: str
    identity: str
    cardinality: int

    @property
    def kind(self) -> str:
        """The vocabulary logical form."""
        return "external"

    def declaration(self) -> dict[str, object]:
        """Return the canonical vocabulary declaration."""
        return {
            "kind": "external",
            "ref": self.ref,
            "identity": self.identity,
            "cardinality": self.cardinality,
        }


Vocabulary = AnonymousVocabulary | ExternalVocabulary


@dataclass(frozen=True, slots=True)
class CategoricalField:
    """An immutable, conforming ``categorical-field/v1`` record.

    ``domain`` is the complete ambient-domain declaration; ``vocabulary`` is the
    immutable vocabulary declaration; ``observation_ids`` is the total categorical
    assignment in canonical ambient-position order (shape ``(P,)``, every value in
    ``{0, ..., K - 1}``).
    """

    domain: RectangularRowColumnDomain
    vocabulary: Vocabulary
    observation_ids: tuple[int, ...]

    @property
    def schema_ref(self) -> str:
        """The canonical logical record schema reference."""
        return SCHEMA_REF

    @property
    def value_kind(self) -> str:
        """Fixed schema semantics: ``categorical``."""
        return VALUE_KIND

    @property
    def coverage(self) -> str:
        """Fixed schema semantics: ``total``."""
        return COVERAGE

    @property
    def persistent(self) -> bool:
        """Fixed schema semantics: ``True``."""
        return PERSISTENT

    def content(self) -> dict[str, object]:
        """Return the canonical content projection (domain + vocab + assignment).

        Two fields are content-identical when the domain declarations,
        vocabulary identities, and canonical observation assignments are
        identical.
        """
        return {
            "domain": self.domain.declaration(),
            "vocabulary": self.vocabulary.declaration(),
            "observation_ids": list(self.observation_ids),
        }


def _validate_vocabulary(vocabulary: Vocabulary) -> int:
    """Return the validated cardinality ``K`` or raise."""
    if not isinstance(vocabulary.cardinality, int) or isinstance(vocabulary.cardinality, bool):
        raise CategoricalFieldError(
            f"vocabulary cardinality must be an integer, got {type(vocabulary.cardinality).__name__}"
        )
    if vocabulary.cardinality < 1:
        raise CategoricalFieldError(f"vocabulary cardinality must be >= 1, got {vocabulary.cardinality}")
    return vocabulary.cardinality


def categorical_field(
    domain: RectangularRowColumnDomain,
    vocabulary: Vocabulary,
    observation_ids: Sequence[int],
) -> CategoricalField:
    """Construct a conforming :class:`CategoricalField` from authoritative inputs.

    Accepts a resolved canonical ambient ``domain``, a resolved immutable
    ``vocabulary`` declaration, and ``observation_ids`` in canonical position
    order. Validates every ``CF-REC-00x`` invariant:

    * exactly the ``position_count`` assignments, in canonical position order
      (``CF-REC-002``);
    * every value in ``{0, ..., K - 1}`` (``CF-REC-004``);
    * exactly one immutable vocabulary identity (``CF-REC-005``).

    Raises :class:`CategoricalFieldError` for a length mismatch, an out-of-range
    value, or an invalid domain/vocabulary.
    """
    position_count = domain.position_count
    if len(observation_ids) != position_count:
        raise CategoricalFieldError(
            f"observation_ids length {len(observation_ids)} != position_count {position_count}"
        )
    cardinality = _validate_vocabulary(vocabulary)
    for value in observation_ids:
        if not isinstance(value, int) or isinstance(value, bool):
            raise CategoricalFieldError(f"observation value {value!r} is not a categorical integer")
        if not 0 <= value < cardinality:
            raise CategoricalFieldError(
                f"observation value {value} outside vocabulary domain [0, {cardinality})"
            )
    return CategoricalField(
        domain=domain,
        vocabulary=vocabulary,
        observation_ids=tuple(observation_ids),
    )


__all__ = [
    "AnonymousVocabulary",
    "COVERAGE",
    "CategoricalField",
    "CategoricalFieldError",
    "ExternalVocabulary",
    "PERSISTENT",
    "SCHEMA_REF",
    "VALUE_KIND",
    "Vocabulary",
    "categorical_field",
]
