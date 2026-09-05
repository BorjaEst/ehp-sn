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

import pytest

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


# ---------------------------------------------------------------------------
# Phase-3 framework-side invariants (P3-T1 · G2 · G17)
# ---------------------------------------------------------------------------

# The Phase-3 HPC place-summary figure is research-owned; adding it must not put
# any HPC / place-cell / rate-map / field-centre semantics into ``ehp_sn.figures``.
# These source-level checks are framework ownership, so they live here (the
# framework figure-architecture home) rather than in the research-figure
# behaviour tests.


def test_figure_framework_imports_no_research() -> None:
    """``ehp_sn.figures`` must not import ``ehp_research`` (ARCH-001, P3-T25/G2)."""
    for module in ("contracts.py", "projection.py", "providers.py", "service.py"):
        source = (_EHP_SN_SRC / "figures" / module).read_text(encoding="utf-8")
        import_lines = _import_lines(source)
        assert not any("ehp_research" in line for line in import_lines)


def test_generic_figure_framework_has_no_hpc_semantics() -> None:
    """The generic figure spine carries no HPC / place-cell / rate-map semantics
    (P3-T25 · G17). The only legitimate generic change was the anticipated
    selection-provenance extension (Phase-1 § 12 · P1-T10)."""
    for module in ("contracts.py", "projection.py", "service.py"):
        source = (_EHP_SN_SRC / "figures" / module).read_text(encoding="utf-8")
        for token in (
            "hpc-place-summary",
            "spatial_information",
            "rate_map",
            "field_centre",
            "place cell",
            "gridness",
        ):
            assert token not in source


def test_generic_figure_service_has_no_hpc_branch() -> None:
    """The generic figure service has no HPC / spatial-information logic (P3-T25).

    Complements the Phase-1 ``test_figure_service_has_no_producer_or_raster_branching``
    for the Phase-3 research figure.
    """
    source = (_EHP_SN_SRC / "figures" / "service.py").read_text(encoding="utf-8")
    for token in (
        "hpc",
        "hpc-place-summary",
        "spatial_information",
        "rate_map",
        "field_centre",
        "place cell",
        "gridness",
    ):
        assert token not in source


# ---------------------------------------------------------------------------
# Phase-4 framework-side invariants (P4-T1..T8, P4-7, P4-11)
# ---------------------------------------------------------------------------

# Phase 4 adds realization, presentation, and serialization machinery to
# ``ehp_sn.figures``. These source-level checks hold the framework ownership
# boundary: the new realization/serialization/presentation modules must not
# import research, must not introduce scientific semantics, and must not create
# a figure-specific artifact/resource/digest hierarchy (Phase-4 § 21, P4-11).

_PHASE4_REALIZATION_MODULES = (
    "realization.py",
    "render_profile.py",
    "serialization.py",
    "persistence.py",
)


def test_phase4_modules_import_no_research() -> None:
    """The new Phase-4 figure modules must not import ``ehp_research`` (ARCH-001)."""
    for module in _PHASE4_REALIZATION_MODULES:
        source = (_EHP_SN_SRC / "figures" / module).read_text(encoding="utf-8")
        import_lines = _import_lines(source)
        assert not any("ehp_research" in line for line in import_lines)


def test_phase4_realization_modules_have_no_scientific_semantics() -> None:
    """Realization/presentation/serialization code carries no scientific meaning.

    These modules own ``how`` an already-fixed projection is communicated, not
    ``what`` scientific view it is (Phase-4 § 4; ``rendering.md`` §
    ``RenderProfile`` / "Serialization request"). They must name no research
    figure, metric, or scientific selection concept.
    """
    for module in _PHASE4_REALIZATION_MODULES:
        source = (_EHP_SN_SRC / "figures" / module).read_text(encoding="utf-8")
        for token in (
            "rate_map",
            "spatial_information",
            "field_centre",
            "place cell",
            "gridness",
            "top-k",
        ):
            assert token not in source


def _public_names(module_path: pathlib.Path) -> set[str]:
    """Return the names a module exports (``__all__`` plus module-level names).

    Inspects only the implementation surface (exports and defined symbols), not
    docstrings/comments, so prose discussing an excluded concept does not trip
    the check.
    """
    import ast

    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    all_names: set[str] | None = None
    assign_names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "__all__" and isinstance(node.value, (ast.List, ast.Tuple)):
                        all_names = {el.value for el in node.value.elts if isinstance(el, ast.Constant)}
                    else:
                        assign_names.add(target.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            assign_names.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                assign_names.add((alias.asname or alias.name).split(".")[0])
    return assign_names if all_names is None else set(all_names)


def test_phase4_serialization_exposes_no_filename_save_entry_point() -> None:
    """Serialization policy requires an explicit format; no filename path exists.

    Phase-4 § 4 (P4-T3): no identity-affecting serialization parameter may be
    inferred from a filename extension or ambient Matplotlib defaults. The
    serialization module's public surface must expose no path/filename save
    entry point — only explicit-format policy resolution.
    """
    names = _public_names(_EHP_SN_SRC / "figures" / "serialization.py")
    for token in ("savefig", "save", "write_figure", "to_file"):
        assert token not in names
    # The supported formats are explicit constants.
    assert "SUPPORTED_FORMATS" in names
    assert "resolve_serialization_policy" in names


def test_no_figure_specific_artifact_or_persistence_hierarchy() -> None:
    """The figure package introduces no FigureArtifact/FigureStore hierarchy (P4-11).

    The framework realization path produces serialized bytes plus generic content
    integrity; it must not introduce a figure artifact kind, a figure store, a
    figure resource registry, a figure-specific digest architecture, or a
    figure-specific staging/commit lifecycle (Phase-4 § 21; `integration.md` §
    "Destination and sinks"). Inspects the exported/symbol surface, not prose.
    """
    modules = (
        "contracts.py",
        "projection.py",
        "service.py",
        "realization.py",
        "render_profile.py",
        "serialization.py",
        "persistence.py",
    )
    for module in modules:
        names = _public_names(_EHP_SN_SRC / "figures" / module)
        for token in (
            "FigureArtifact",
            "FigureStore",
            "FigureResourceRegistry",
            "FigureSchedule",
            "FigureComposition",
        ):
            assert token not in names


def test_phase4_persistence_introduces_no_figure_lifecycle() -> None:
    """The persistence boundary adds no figure-specific staging/commit lifecycle.

    Phase-4B waits for a real persistent owner; the framework must not invent a
    figure-specific persistence system (Phase-4 § 10/§ 16, P4-11). The
    persistence module's public surface exports only a generic content-integrity
    check and its error.
    """
    names = _public_names(_EHP_SN_SRC / "figures" / "persistence.py")
    assert names == {"FigureContentIntegrityError", "verify_content_digest"}
    for token in ("stage", "commit", "publish", "Store", "FigureStore"):
        assert token not in names


def test_provider_figure_has_no_savefig_persistence_logic() -> None:
    """Scientific renderers must not perform provider-local ``savefig`` (P4-7).

    Serialization must occur through one controlled framework path
    (``rendering.md`` § "Serialization request"; Phase-4 · P4-T6/P4-T7). A
    scientific figure's visual implementation must draw and return a Figure,
    leaving serialization to the framework; ``savefig`` must not appear in
    provider figure code.
    """
    from ehp_sn.figures.builtin import raster_topology as rt

    source = pathlib.Path(rt.__file__).read_text(encoding="utf-8")
    assert "savefig" not in source


def test_figures_reuse_generic_framework_content_integrity() -> None:
    """Content integrity reuses the generic digests home (Phase-4 · P4-T13).

    The figure realization and persistence modules digest serialized bytes via
    the generic ``ehp_sn.digests.sha256_bytes_digest`` and define no figure-local
    hashing algorithm.
    """
    import ast

    realization_src = (_EHP_SN_SRC / "figures" / "realization.py").read_text(encoding="utf-8")
    persistence_src = (_EHP_SN_SRC / "figures" / "persistence.py").read_text(encoding="utf-8")
    # Both modules use the generic byte-digest mechanism.
    assert "sha256_bytes_digest" in realization_src
    assert "sha256_bytes_digest" in persistence_src
    # No module defines its own private hashing function.
    for src in (realization_src, persistence_src):
        tree = ast.parse(src)
        for node in tree.body:
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name.startswith("_")
                and "digest" in node.name.lower()
            ):
                raise AssertionError(f"figure-local digest routine {node.name!r} must not exist")


def test_no_speculative_identity_placeholders() -> None:
    """Realization identity carries no speculative layout/binding placeholders
    (Phase-4 · P4-T20).

    Only implemented semantics appear in ``RealizationIdentity``; a planned
    concept must not harden as a stable public placeholder field.
    """
    import ast

    src = (_EHP_SN_SRC / "figures" / "realization.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RealizationIdentity":
            fields = {
                a.target.id
                for a in node.body
                if isinstance(a, ast.AnnAssign) and isinstance(a.target, ast.Name)
            }
            assert "layout_identity" not in fields
            assert "panel_binding_identity" not in fields


def test_single_canonical_realization_resolution_boundary() -> None:
    """There is exactly one resolved-realization boundary (Phase-4 · P4-T9)."""
    names = _public_names(_EHP_SN_SRC / "figures" / "realization.py")
    assert "resolve_figure_realization" in names
    assert "ResolvedFigureRealization" in names


# --------------------------------------------------------------------------- #
# Phase-5 — artifact-metadata surfaces and qualification stay producer-blind
# --------------------------------------------------------------------------- #


def test_phase5_source_surface_module_has_no_producer_names() -> None:
    """``figures/source.py`` (the artifact-metadata surface vocabulary) is producer-blind.

    The surface vocabulary and its ``ArtifactSourceContent`` carriage must not
    name any producer family; only the owning research figure interprets a
    producer value (Phase-5 § 22 · ARCH-001).
    """
    src = (_EHP_SN_SRC / "figures" / "source.py").read_text(encoding="utf-8")
    for token in ("dagflow", "maze-nd", "dungeongen", "obsfield", "arena"):
        assert token not in src
    # The framework vocabulary is fixed and admits exactly the three surfaces.
    assert "producer-descriptors" in src
    assert "provenance" in src
    assert "auxiliary" in src
    # The surfaced content carries records plus opaque metadata, never a producer type.
    assert "LogicalRecord" in src
    assert "ProducerDescriptor" in src


def test_figure_requirement_surface_validation_is_generic() -> None:
    """``FigureInputRequirement`` validates the surface vocabulary without producers.

    The requirement admits only the framework-declared surface names and requires
    artifact scope; it performs no producer dispatch (Phase-5 § 1, § 17).
    """
    from ehp_sn.figures.contracts import FigureInputRequirement
    from ehp_sn.figures.scope import SCOPE_ARTIFACT
    from ehp_sn.figures.source import ARTIFACT_METADATA_SURFACES

    req = FigureInputRequirement(
        role="g",
        contract="simple-digraph/v1",
        scope=SCOPE_ARTIFACT,
        artifact_metadata_surfaces=frozenset({"producer-descriptors", "provenance", "auxiliary"}),
    )
    assert req.artifact_metadata_surfaces == ARTIFACT_METADATA_SURFACES
    # The framework surface vocabulary contains no producer name.
    assert all(
        "dagflow" not in s and "dungeongen" not in s and "obsfield" not in s
        for s in ARTIFACT_METADATA_SURFACES
    )


def test_phase5_qualification_module_is_producer_blind() -> None:
    """The qualification/review module (Stage F) models only status vocabulary.

    It records outcomes and resolves the § 43 precedence rule; it must not name
    a producer, a producer configuration type, or a concrete specification
    (Phase-5 § 36-43).
    """
    src = (_EHP_SN_SRC / "qualification.py").read_text(encoding="utf-8")
    for token in ("dagflow", "maze-nd", "dungeongen", "obsfield", "Dagflow", "DungeonGen"):
        assert token not in src
    # The § 43 precedence rule is present and generic.
    assert "QualificationStatus" in src
    assert "ReviewOutcome" in src
    assert "AnomalyDisposition" in src


# ---------------------------------------------------------------------------
# Phase 7C § 8/6/14 — source-resolution, dependency-direction, and
# scientific-authority source guards (generic figure layer)
# ---------------------------------------------------------------------------


def _figures_pkg_path() -> pathlib.Path:
    return _EHP_SN_SRC / "figures"


def test_figure_layer_has_no_resolver_or_fingerprint_vocabulary() -> None:
    """The generic figure layer owns no artifact/record search or storage root.

    Figure code must reuse generic data/resource infrastructure (Phase 7C § 8).
    This structural guard asserts the generic figure modules introduce none of
    the vocabulary a figure-owned resolver would need: no artifact search, record
    search, source fingerprinting, storage root, or artifact identity routing.
    """
    forbidden = (
        "find_record",
        "search_artifact",
        "fingerprint",
        "storage_root",
        "index_dir",
        "readdir",
        "scan_release",
        "locate_artifact",
    )
    for module in ("service", "source", "providers", "api", "projection"):
        text = (_figures_pkg_path() / f"{module}.py").read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{module}.py contains figure-owned resolver vocabulary {token!r}"


def test_figure_layer_reuses_generic_artifact_resolution() -> None:
    """Figure orchestration delegates artifact resolution to the generic layer."""
    service_text = (_figures_pkg_path() / "service.py").read_text(encoding="utf-8")
    assert "ehp_sn.artifacts" in service_text
    assert "load_release" in service_text


def test_generic_orchestration_has_no_model_or_task_specialization() -> None:
    """Generic figure orchestration must not name model or task specialization.

    Phase 7C § 6 requires generic orchestration independent of producer, task,
    *and* model specialization; this extends the producer/task guard to concrete
    model vocabulary (HRM, TEM) and task-family vocabulary (MazeHard).
    """
    from ehp_sn.figures import service as service_module

    text = pathlib.Path(service_module.__file__).read_text(encoding="utf-8")
    for token in ("HRM", "TEM", "MazeHard", "HrmLatent", "MazeHardCaseData"):
        assert token not in text, f"generic orchestration names model/task specialization {token!r}"


_ACCEPTANCE_VOCABULARY = (
    "p-value",
    "significance",
    "hypothesis",
    "acceptance_evidence",
    "accepted_artifact",
    "sig=",
)


def test_figure_code_establishes_no_acceptance_evidence() -> None:
    """Figure code never computes or asserts acceptance evidence.

    Category-C scientific/data-quality evidence (acceptance, significance,
    hypothesis testing) must be owned by validator / data-quality / analysis /
    evaluation authority. Figure code may visualize such evidence but must not
    establish it (Phase 7C § 14; ``record-inspection-conformance.md`` SRF-015).
    """
    for module in _figures_pkg_path().rglob("*.py"):
        lowered = module.read_text(encoding="utf-8").lower()
        for token in _ACCEPTANCE_VOCABULARY:
            assert token not in lowered, (
                f"{module.relative_to(_figures_pkg_path())} contains acceptance-"
                f"evidence vocabulary {token!r}"
            )


def test_mazehard_case_figure_absent_from_generic_catalogue() -> None:
    """The MazeHard task-layer figure does not enter the generic catalogue.

    Scenario C (Phase 7E § 29): an experiment/task-local joint figure is reached
    directly, not auto-resolved through ``effective_figure_registry()``. The
    generic catalogue must not contain it (no generic figure semantics change).
    """
    from ehp_sn.figures import effective_figure_registry

    refs = {d.ref.canonical for d in effective_figure_registry().iter(kind="figure")}
    assert "figure:maze-hard-case/v1" not in refs
