"""Phase-1 figure architecture invariants.

These source-level structural checks enforce the Phase-1 walking-skeleton
architectural claims (docs/docs/architecture/figures.md § "Bootstrap
implementation slice"; Phase-1 § 18, § 23):

* generic figure orchestration (``ehp_sn.figures.service``) must contain no
  producer-family and no raster-contract semantic branching;
* the generic data-inspection adapter (``ehp_sn.cli.data_adapter``) stays
  figure-free: its exact-record textual inspection path introduces no figure
  framework import (Phase-1 § 15, preserving P0R architecture);
* the framework figure provider contributes through the ordinary component
  catalogue (kind ``figure``) and introduces no parallel authoritative registry;
* the raster figure lives in ``ehp_sn`` only because its meaning is expressible
  purely through the framework-owned ``raster-topology/v1`` contract.

These complement the runtime behaviour tests in
``packages/ehp-sn/tests/figures/test_phase1_figure_skeleton.py``.
"""

from __future__ import annotations

import pathlib

_PACKAGES_ROOT = pathlib.Path(__file__).resolve().parents[2] / "packages"
_EHP_SN_SRC = _PACKAGES_ROOT / "ehp-sn" / "src" / "ehp_sn"


def _import_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.lstrip().startswith(("import ", "from "))]


def _notebook_code_lines(text: str) -> list[str]:
    """Return lines that are code (drop blank and docstring/comment-only lines)."""
    return [line for line in text.splitlines() if line.strip()]


def test_figure_service_has_no_producer_or_raster_branching() -> None:
    """Generic figure orchestration must not branch on producer or raster contracts.

    The figure service resolves a ``FigureSpec`` through the ordinary catalogue
    and delegates contract-specific behavior to the ``FigureSpec`` itself. It
    must not name a producer family, and must not import or dispatch on a
    concrete builtin figure (Phase-1 § 18).
    """
    from ehp_sn.figures import service as service_module

    source = pathlib.Path(service_module.__file__).read_text(encoding="utf-8")
    # No producer-family token anywhere in orchestration code.
    for token in ("dagflow", "maze-nd", "dungeongen", "obsfield"):
        assert token not in source
    # No direct import of a builtin figure from generic orchestration, and no
    # conditional dispatch on a contract.
    assert not any("ehp_sn.figures.builtin" in line for line in _import_lines(source))
    # The service must resolve generically by kind; it must not special-case a
    # figure name or a contract as orchestration logic.
    assert "raster-topology-inspection" not in source
    assert "if contract ==" not in source


def _single_tokens(text: str) -> list[str]:
    """Return every whitespace-delimited token of source (code + comments)."""
    return text.split()


def test_data_adapter_stays_figure_free() -> None:
    """The generic exact-record inspection adapter remains figure-free (P0R).

    ``data inspect`` textual inspection (``inspect``) delegates no figure
    framework import; figure semantics are additive and owned downstream in the
    figure service, not in the generic inspection adapter (Phase-1 § 15/17).
    """
    from ehp_sn.cli import data_adapter

    source = pathlib.Path(data_adapter.__file__).read_text(encoding="utf-8")
    import_lines = [
        line for line in source.splitlines() if line.lstrip().startswith(("import ", "from "))
    ]
    assert not any(
        line.lstrip().startswith(("from ehp_sn.figures", "from matplotlib", "import matplotlib"))
        for line in import_lines
    )
    for token in ("FigureSpec", "FigureProjection", "matplotlib", "renderer"):
        assert token.lower() not in source.lower()


def test_figure_registry_uses_ordinary_catalogue_not_parallel_registry() -> None:
    """Figure resolution uses the ordinary ComponentRegistry (kind ``figure``).

    Phase-1 must introduce no parallel authoritative figure registry. The
    framework contributes built-in figures through a provider that registers
    them into the same generic ``ComponentRegistry`` class. Removing a built-in
    figure from its provider makes ordinary catalogue resolution fail — there is
    no second registry to re-resolve it.
    """
    from ehp_sn.discovery import ComponentRegistry
    from ehp_sn.experiments import ComponentRef
    from ehp_sn.figures.providers import register_builtin_figures

    registry = ComponentRegistry()
    register_builtin_figures(registry)
    definition = registry.resolve("figure:raster-topology-inspection/v1")
    assert definition.kind == "figure"

    # An empty ordinary catalogue cannot resolve the figure: no parallel
    # registry remains to re-resolve it after provider removal.
    empty = ComponentRegistry()
    from ehp_sn.discovery import UnknownReferenceError

    raised = False
    try:
        empty.resolve(ComponentRef.parse("figure:raster-topology-inspection/v1"))
    except UnknownReferenceError:
        raised = True
    assert raised


def test_raster_figure_has_no_producer_semantics() -> None:
    """The raster figure must not depend on producers or their vocabulary.

    Phase-1 § 6 (P1-T4): the raster inspection figure's semantics are
    expressible purely through the framework-owned ``raster-topology/v1``
    contract. It must not import a research package or a producer, and must not
    branch on producer identity.
    """
    from ehp_sn.figures.builtin import raster_topology as rt

    source = pathlib.Path(rt.__file__).read_text(encoding="utf-8")
    import_lines = _import_lines(source)
    # No research/producer import and no concrete substrate-package import.
    assert not any("ehp_research" in line for line in import_lines)
    assert not any("substrates" in line for line in import_lines)
    # The figure's declared input requirement is exactly the framework-owned
    # raster-topology/v1 contract, not a producer or physical-storage detail.
    requirement = rt.RASTER_TOPOLOGY_INSPECTION_FIGURE.projection.requirement
    assert requirement.role == "topology"
    assert requirement.contract == "raster-topology/v1"
