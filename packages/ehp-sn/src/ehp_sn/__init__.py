"""EHP-SN framework package.

Reusable framework contracts and services. Concrete scientific definitions and
experiments live elsewhere (``docs/authority.md``); this package holds no
concrete research component (``ARCH-001``/``ARCH-006``).

Submodules expose the public surface at their documented locations, for
example ``from ehp_sn.experiments import ExperimentRef, resolve_experiment``.
The top-level package deliberately keeps an empty ``__all__``: public symbols
are re-exported from their owning submodules rather than flattened here
(design decision G-02).
"""

from __future__ import annotations

__all__: list[str] = []
