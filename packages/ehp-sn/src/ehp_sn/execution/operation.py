"""Generic producer execution operation (Capability 9).

This module defines the narrow, demonstrated producer-side execution operation
that lets ``ehp_sn`` orchestrate one substrate build without importing a
concrete research package or knowing how a family generates records.

The genuinely demonstrated producer-side execution operation is:

.. code-block:: text

    framework-controlled uncommitted materialization session
            ↓
    producer scientific execution
            ↓
    populated session (records + auxiliary logical resources)

It is represented by the single typed callable :data:`ExecutionOperation`
(``Callable[[MaterializationSession], None]``). A producer supplies one such
callable per registered definition; the execution composition binds it to the
authoritative definition object.

The producer owns the scientific inner loop entirely: whether it generates
record by record, source-wide, in batches, with retries, or with deduplication.
The framework orchestrates one substrate build operation; it does **not**
orchestrate the scientific inner record-generation loop. The producer populates
the framework-owned session and returns nothing; publication and release
coordinate selection are never the producer's responsibility.
"""

from __future__ import annotations

from collections.abc import Callable

from .materialization import MaterializationSession

#: The typed producer execution operation bound to a registered definition.
#:
#: It receives the framework-controlled uncommitted
#: :class:`~ehp_sn.execution.materialization.MaterializationSession`, seeded from
#: the authoritative plan, and populates it with generated record bodies and
#: auxiliary logical resources. It returns ``None``: the framework owns the
#: session and any subsequent artifact lifecycle. Only the producer's scientific
#: content is deliberately opaque to the framework.
type ExecutionOperation = Callable[[MaterializationSession], None]


__all__ = ["ExecutionOperation"]
