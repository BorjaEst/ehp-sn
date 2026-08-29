"""Integration tests — real installed figure-provider discovery (Phase 2).

This is the root-level integration scope for the Phase-2 provider-extension
seam with **no mocks**:

```text
installed package metadata (test-figure-provider)
        ↓
importlib.metadata discovery (ehp_sn.figures.providers)
        ↓
provider
        ↓
ordinary component catalogue
```

It proves the actual extension seam (Phase-2 § 16.2, § 23, P2-12): an installed
external distribution's advertised provider is discovered through the real
``importlib.metadata`` mechanism and contributes its figures to the ordinary
component catalogue. Mocks are deliberately not used here; unit-level provider
semantics with fake/injected entry points live in
``packages/ehp-sn/tests/figures/test_figure_provider_cardinality.py``.

This module is scoped to **discovery and catalogue contribution**. Real
committed-artifact figure rendering lives in
``tests/integration/test_data_inspect_figure.py``.

It skips when the fixture distribution ``test-figure-provider`` is not installed,
mirroring the existing research-provider and committed-artifact integration test
pattern.
"""

from __future__ import annotations

from importlib import metadata

import pytest
from ehp_sn.figures import effective_figure_registry
from ehp_sn.figures.providers import FIGURE_PROVIDER_ENTRY_POINT_GROUP

_GRAPH_REF = "figure:simple-digraph-inspection/v1"
_RASTER_REF = "figure:raster-topology-inspection/v1"


def _has_test_provider() -> bool:
    """Whether the real installed test-figure-provider distribution is present."""
    try:
        eps = list(metadata.entry_points(group=FIGURE_PROVIDER_ENTRY_POINT_GROUP))
    except Exception:  # pragma: no cover - resilient to metadata read errors
        return False
    return any("test_figure_provider" in ep.value for ep in eps)


REQUIRES_PROVIDER = pytest.mark.skipif(
    not _has_test_provider(),
    reason="test-figure-provider fixture distribution is not installed",
)


# ---------------------------------------------------------------------------
# P2-B / P2-12 — real installed package metadata discovery (no mocks)
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_real_installed_provider_entry_point_is_discoverable() -> None:
    """The installed distribution advertises a provider under the canonical group.

    This uses the **real** ``importlib.metadata`` discovery — not a fake entry
    point — proving an installed external package can contribute figures
    (P2-12 / § 16.2).
    """
    eps = list(metadata.entry_points(group=FIGURE_PROVIDER_ENTRY_POINT_GROUP))
    assert any("test_figure_provider" in ep.value for ep in eps), (
        "test-figure-provider advertises no figure provider"
    )


@REQUIRES_PROVIDER
def test_real_provider_contributes_external_figure_to_catalogue() -> None:
    """The installed provider's external graph figure enters the ordinary catalogue.

    The built-in raster figure and the external graph figure resolve through the
    same ordinary catalogue and the same canonical API (P2-C / P2-3), regardless
    of package origin.
    """
    registry = effective_figure_registry()
    definition = registry.resolve(_GRAPH_REF)
    assert definition.kind == "figure"
    assert registry.resolve(_RASTER_REF).kind == "figure"
