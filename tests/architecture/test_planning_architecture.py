"""Architecture invariants for Phase 3B Capability 6 — generic substrate planning.

These tests enforce that the generic planning layer (``ehp_sn.planning``) stays
framework-owned and generic:

* it must not import ``ehp_research`` (ARCH-001 direction) nor ``ehp_sn.cli``
  (no exit-code / interface semantics);
* it must contain no substrate-family names (Dagflow / Maze-ND) and no
  family dispatch, so the framework never special-cases a producer;
* the planning orchestration must consume generic requirements, never branch on
  a resolved producer configuration type.

These are source-level structural checks, independent of runtime behavior.
"""

from __future__ import annotations

import pathlib

_PACKAGES_ROOT = pathlib.Path(__file__).resolve().parents[2] / "packages"
_EHP_SN_SRC = _PACKAGES_ROOT / "ehp-sn" / "src" / "ehp_sn"
_PLANNING_SRC = _EHP_SN_SRC / "planning"


def _py_files(root: pathlib.Path) -> list[pathlib.Path]:
    return [p for p in root.rglob("*.py") if p.is_file()]


def _import_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.lstrip().startswith(("import ", "from "))]


def test_planning_never_imports_ehp_research() -> None:
    """The generic planning layer must not depend on a concrete research package."""
    offenders: list[str] = []
    for file in _py_files(_PLANNING_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        if any("ehp_research" in line for line in import_lines):
            offenders.append(str(file))
    assert offenders == [], f"ehp_sn.planning must not import ehp_research; found in: {offenders}"


def test_planning_does_not_depend_on_cli() -> None:
    """Planning carries no exit-code / interface semantics."""
    offenders: list[str] = []
    for file in _py_files(_PLANNING_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        for line in import_lines:
            if "ehp_sn.cli" in line:
                offenders.append(f"{file}: {line.strip()}")
    assert offenders == [], f"ehp_sn.planning must not depend on ehp_sn.cli; found: {offenders}"


def test_planning_has_no_substrate_family_names() -> None:
    """The generic planning layer must not know Dagflow or Maze-ND."""
    for file in _py_files(_PLANNING_SRC):
        text = file.read_text(encoding="utf-8")
        assert "dagflow" not in text.lower(), file
        assert "maze-nd" not in text.lower(), file
        assert "maze_nd" not in text.lower(), file


def test_orchestration_has_no_producer_branching() -> None:
    """plan_substrate must consume generic requirements, never branch on a producer.

    The orchestration source must not reference any producer configuration type
    name, and must treat the producer configuration strictly opaquely: it never
    dereferences a field on the resolved configuration object (no
    ``configuration.<field>`` / ``configuration[<key>]`` access) and performs no
    ``isinstance`` dispatch on it. It only passes the configuration whole onto
    the plan. (Legitimate generic dispatches — normalizing a string to a
    ``ComponentRef`` or checking ``definition.kind`` — are not producer
    branching.)
    """
    orchestration = (_PLANNING_SRC / "orchestration.py").read_text(encoding="utf-8")

    # No producer config type names anywhere.
    for producer_token in ("DagflowConfiguration", "MazeNDConfiguration"):
        assert producer_token not in orchestration

    # No dispatch on or dereference of a producer configuration object.
    # ``declaration.configuration`` appears only as the whole opaque value being
    # passed to the plan; any attribute/index access on the configuration (the
    # research-leakage vector) is forbidden.
    assert "declaration.configuration." not in orchestration
    assert "configuration[" not in orchestration
    for family in ("dagflow", "maze_nd", "maze-nd"):
        assert family not in orchestration.lower()


def test_planning_adds_no_placeholder_types() -> None:
    """Capability 6 introduces no production placeholders or pending-plan types."""
    import re

    forbidden = (
        "PlaceholderExecutionPlan",
        "PlaceholderResourceResolver",
        "PlaceholderIdentityResolver",
        "PendingBuildPlan",
        "FakeProducerCapability",
        "SubstratePlanner",
        "PlanningService",
        "ProducerFactory",
        "SubstrateBuildPlan",
        "DataBuildPlan",
        "ResolvedSubstratePlan",
    )
    for file in _py_files(_PLANNING_SRC):
        text = file.read_text(encoding="utf-8")
        for token in forbidden:
            assert re.search(rf"\b{re.escape(token)}\b", text) is None, (
                f"{file} must not introduce {token!r}"
            )
