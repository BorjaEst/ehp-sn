"""EHP-SN framework-owned standard scientific data contracts.

This package owns the shared *logical record schemas* that concrete research
producers emit and concrete task consumers read, as specified under
``docs/docs/framework/contracts/`` (the authoritative home for their semantics).
A contract defines one reusable, producer-agnostic, consumer-agnostic semantic
object — for example a simple directed graph, an ambient spatial domain, a
categorical observation field, or a raster topology — together with its
authoritative representation, its canonical derived views, and its schema-level
invariants.

This package is framework-owned (``ARCH-001``): it imports no concrete research
package and must remain meaningful if ``ehp_research`` did not exist. Concrete
substrate families (in ``ehp_research``) produce records that conform to these
contracts; they never redefine them.

Public symbols are re-exported from their owning submodules rather than
flattened here (design decision ``G-02``). The registered contracts are:

* :mod:`ehp_sn.contracts.relations` — ``simple-digraph/v1``;
* :mod:`ehp_sn.contracts.domains` — ``rectangular-row-column/v1``
  (registered ambient-domain schema);
* :mod:`ehp_sn.contracts.observations` — ``categorical-field/v1``;
* :mod:`ehp_sn.contracts.topology` — ``raster-topology/v1``.
"""

from __future__ import annotations

__all__: list[str] = []
