"""Architecture invariants for Phase 4 Capability 9 — generic substrate execution.

These tests enforce that the generic execution layer (``ehp_sn.execution``) stays
framework-owned and generic:

* it must not import ``ehp_research`` (ARCH-001 direction) nor ``ehp_sn.cli``
  (no exit-code / interface semantics);
* it must contain no substrate-family names (Dagflow / ObsField / Maze-ND /
  DungeonGen) and no family dispatch, so the framework never special-cases a
  producer;
* the execution orchestration must consume generic requirements, never branch on
  a resolved producer configuration type, and must not assume intrinsic splits,
  record-at-a-time generation, raster topology, or an absence of auxiliary
  resources;
* it must introduce no production placeholder service/engine/factory names.

These are source-level structural checks, independent of runtime behavior.
"""

from __future__ import annotations

import pathlib
import re

_PACKAGES_ROOT = pathlib.Path(__file__).resolve().parents[2] / "packages"
_EHP_SN_SRC = _PACKAGES_ROOT / "ehp-sn" / "src" / "ehp_sn"
_EXECUTION_SRC = _EHP_SN_SRC / "execution"


def _py_files(root: pathlib.Path) -> list[pathlib.Path]:
    return [p for p in root.rglob("*.py") if p.is_file()]


def _import_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.lstrip().startswith(("import ", "from "))]


def test_execution_never_imports_ehp_research() -> None:
    """The generic execution layer must not depend on a concrete research package."""
    offenders: list[str] = []
    for file in _py_files(_EXECUTION_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        if any("ehp_research" in line for line in import_lines):
            offenders.append(str(file))
    assert offenders == [], f"ehp_sn.execution must not import ehp_research; found in: {offenders}"


def test_execution_does_not_depend_on_cli() -> None:
    """Execution carries no exit-code / interface semantics."""
    offenders: list[str] = []
    for file in _py_files(_EXECUTION_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        for line in import_lines:
            if "ehp_sn.cli" in line:
                offenders.append(f"{file}: {line.strip()}")
    assert offenders == [], f"ehp_sn.execution must not depend on ehp_sn.cli; found: {offenders}"


def test_execution_has_no_substrate_family_names() -> None:
    """The generic execution layer must not know Dagflow, ObsField, Maze-ND, or DungeonGen."""
    forbidden = ("dagflow", "obsfield", "maze-nd", "maze_nd", "dungeongen")
    for file in _py_files(_EXECUTION_SRC):
        text = file.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text, f"{file} must not contain family token {token!r}"


def test_orchestration_has_no_producer_branching() -> None:
    """execute_substrate must consume generic plans, never branch on a producer.

    The orchestration source must not reference any producer configuration type
    name, must not dereference a field on the opaque producer configuration
    carried by the plan (no ``plan.configuration.<field>`` /
    ``configuration[<key>]`` access), and must not perform ``isinstance``
    dispatch on it. The whole opaque configuration may be forwarded onto the
    materialization session, never inspected.
    """
    for file in _py_files(_EXECUTION_SRC):
        text = file.read_text(encoding="utf-8").lower()
        for producer_token in ("dagflow", "obsfield", "maze_nd", "maze-nd", "dungeongen"):
            assert producer_token not in text, f"{file} must not contain {producer_token!r}"

    orchestration = (_EXECUTION_SRC / "orchestration.py").read_text(encoding="utf-8")
    # The whole opaque producer configuration may be forwarded, but no field on
    # it and no index into it may be read (the research-leakage vector).
    assert "plan.configuration." not in orchestration
    assert "configuration[" not in orchestration
    assert "isinstance(" not in orchestration


def test_execution_adds_no_placeholder_or_bad_boundary_types() -> None:
    """Capability 9 introduces no production placeholders or provider-bag types."""
    forbidden = (
        "SubstrateProvider",
        "BuildEngine",
        "ProducerFactory",
        "CapabilityDictionary",
        "DagflowBuilder",
        "RasterBuilder",
        "TopologyBuilder",
        "CategoricalBuilder",
        "SourceImporter",
        "SplitManager",
        "RetryManager",
        "Deduplicator",
    )
    for file in _py_files(_EXECUTION_SRC):
        text = file.read_text(encoding="utf-8")
        for token in forbidden:
            assert re.search(rf"\b{re.escape(token)}\b", text) is None, (
                f"{file} must not introduce {token!r}"
            )


def test_execution_digest_comes_from_framework_wide_home() -> None:
    """Record identity uses the framework-wide digest, not a planning utility.

    Target 0 (canonical digest ownership): the exact JCS canonicalization and
    digest operation live in ``ehp_sn.digests`` and are shared across lifecycle
    stages; execution must not depend conceptually on a planning-specific
    utility. This checks that record identity's digest import points at
    ``ehp_sn.digests`` and that planning does not re-export the digest
    primitives it does not own.
    """
    record_identity = (_EXECUTION_SRC / "record_identity.py").read_text(encoding="utf-8")
    # Record identity imports the digest mechanism from the framework-wide home.
    assert "from ehp_sn.digests import" in record_identity
    # It must not import a digest primitive from planning (planning is plan-only).
    planning_import = record_identity.split("from ehp_sn.planning import", 1)
    if len(planning_import) > 1:
        planning_line = planning_import[1].splitlines()[0]
        assert "canonical_digest" not in planning_line

    planning_init = (_EHP_SN_SRC / "planning" / "__init__.py").read_text(encoding="utf-8")
    # planning no longer owns the generic digest primitives.
    assert "canonical_digest" not in planning_init
    assert "canonicalize" not in planning_init
