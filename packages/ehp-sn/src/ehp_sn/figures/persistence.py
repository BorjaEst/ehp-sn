"""Figure persistence boundary (Phase-4B — explicitly deferred, State B).

Phase 4A (realization) makes a serialized realization *persistence-ready*: a
:class:`~ehp_sn.figures.realization.RealizedFigure` carries the exact serialized
bytes, their :class:`~ehp_sn.figures.realization.ContentDigest` (in the standard
framework ``sha256:`` integrity form), the semantic
:class:`~ehp_sn.figures.realization.RealizationIdentity`, and distinct rendering
environment provenance.

## Phase-4B completion state

Per Phase-4 § 10/§ 16 and P4-T19, there are only two valid persistence states:

```text
State A — a suitable resource owner exists
    then Phase 4B demonstrates:
        serialized realization → real owner staging → generic integrity → commit

State B — no suitable resource owner exists
    then Phase 4A is complete and Phase 4B is explicitly deferred
```

The current repository has **no** report / analysis / export resource owner with
a staged↔committed lifecycle (the only committed-artifact mechanism is the
substrate release store, which is substrate-typed and would be an inappropriate
owner for a serialized figure). Phase 4B is therefore in **State B**: explicitly
deferred until the first real consumer exists. No fake persistence owner is
created merely to make the milestone green, and the complete phase is not
described as fully closed until Phase 4B is exercised by a real consumer.

## Generic content-integrity reuse (Phase-4 · P4-T13)

Content integrity for persisted figure bytes is a **usage** of the generic
framework byte-digest mechanism (:func:`ehp_sn.digests.sha256_bytes_digest`),
not a figure-owned integrity system:

```text
serialized figure bytes
        ↓
generic EHP-SN byte integrity (ehp_sn.digests)
        ↓
figure-facing thin adapter (this module)
```

Wrong:

```text
serialized figure bytes
        ↓
figure-owned hashing algorithm / integrity store
```

This module therefore must **not** introduce:

```text
FigureArtifact
FigureStore
FigureResourceRegistry
a figure-owned hashing algorithm
a figure-specific digest lifecycle / integrity persistence
a figure-specific staging / commit / immutability lifecycle
```

It provides exactly one generic, owner-agnostic helper: verifying that a
:class:`RealizedFigure`'s serialized bytes reproduce their recorded content
digest through the generic framework digest. Any existing resource owner may
reuse it when the figure is persisted.
"""

from __future__ import annotations

from ehp_sn.digests import sha256_bytes_digest
from ehp_sn.figures.realization import RealizedFigure


class FigureContentIntegrityError(ValueError):
    """A realized figure's serialized bytes do not reproduce its content digest."""


def verify_content_digest(realized: RealizedFigure) -> None:
    """Verify that a realized figure's bytes reproduce its recorded content digest.

    Recomputes the ``sha256:`` digest over the exact serialized bytes through the
    generic framework byte-digest mechanism
    (:func:`ehp_sn.digests.sha256_bytes_digest`) and raises
    :class:`FigureContentIntegrityError` on mismatch (or if the recorded digest
    is not a supported ``sha256:`` digest). This is a thin figure-facing adapter
    around generic EHP-SN content integrity (P4-T13); it establishes no
    figure-specific persistence state.
    """
    prefix = "sha256:"
    if not realized.content_digest.value.startswith(prefix):
        raise FigureContentIntegrityError(
            f"unsupported content-digest form {realized.content_digest.value!r}"
        )
    recomputed = sha256_bytes_digest(realized.bytes)
    if recomputed != realized.content_digest.value:
        raise FigureContentIntegrityError(
            "serialized figure bytes do not reproduce the recorded content digest: "
            f"recorded {realized.content_digest.value!r}, recomputed {recomputed!r}"
        )


__all__ = [
    "FigureContentIntegrityError",
    "verify_content_digest",
]
