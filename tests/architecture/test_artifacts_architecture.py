"""Architecture invariants for the generic artifact lifecycle (Phase 4B).

These tests enforce that the generic artifact layer (``ehp_sn.artifacts``)
stays framework-owned, generic, and free of producer/persistence coupling:

* it must not import ``ehp_research`` (ARCH-001) nor ``ehp_sn.cli`` (no
  exit-code/interface semantics);
* it must contain no substrate-family names and no producer-dispatch;
* it must not invoke producer execution (no reference to the execution-callable
  type or to a materialization session's mutating operations from assembly/commit);
* it must not introduce an ``ArtifactStore`` / ``ArtifactWriter`` /
  ``ArtifactRepository`` facade (the user's stated non-goal); persistence is not
  assumed;
* it must not couple to a concrete producer configuration type (no
  ``configuration.<field>`` / ``configuration[`` dereference in assembly).

These are source-level structural checks, independent of runtime behavior.
"""

from __future__ import annotations

import pathlib
import re

_PACKAGES_ROOT = pathlib.Path(__file__).resolve().parents[2] / "packages"
_EHP_SN_SRC = _PACKAGES_ROOT / "ehp-sn" / "src" / "ehp_sn"
_ARTIFACTS_SRC = _EHP_SN_SRC / "artifacts"


def _py_files(root: pathlib.Path) -> list[pathlib.Path]:
    return [p for p in root.rglob("*.py") if p.is_file()]


def _import_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.lstrip().startswith(("import ", "from "))]


def test_artifacts_never_imports_ehp_research() -> None:
    offenders = [
        str(file)
        for file in _py_files(_ARTIFACTS_SRC)
        if any("ehp_research" in line for line in _import_lines(file.read_text(encoding="utf-8")))
    ]
    assert offenders == [], f"ehp_sn.artifacts must not import ehp_research; found in: {offenders}"


def test_artifacts_does_not_depend_on_cli() -> None:
    offenders: list[str] = []
    for file in _py_files(_ARTIFACTS_SRC):
        for line in _import_lines(file.read_text(encoding="utf-8")):
            if "ehp_sn.cli" in line:
                offenders.append(f"{file}: {line.strip()}")
    assert offenders == [], f"ehp_sn.artifacts must not depend on ehp_sn.cli; found: {offenders}"


def test_artifacts_has_no_substrate_family_names() -> None:
    forbidden = ("dagflow", "obsfield", "maze-nd", "maze_nd", "dungeongen")
    for file in _py_files(_ARTIFACTS_SRC):
        text = file.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text, f"{file} must not contain family token {token!r}"


def test_artifact_layer_introduces_no_store_or_writer_facades() -> None:
    """No ArtifactStore / ArtifactWriter / ArtifactRepository invented for persistence."""
    forbidden = ("ArtifactStore", "ArtifactWriter", "ArtifactRepository", "ArtifactLedger")
    for file in _py_files(_ARTIFACTS_SRC):
        text = file.read_text(encoding="utf-8")
        for token in forbidden:
            assert re.search(rf"\b{re.escape(token)}\b", text) is None, (
                f"{file} must not introduce {token!r}"
            )


def test_assembly_does_not_invoke_producer_and_does_not_deref_config() -> None:
    """Assembly consumes plan + materialization; it never executes a producer.

    The assembly source must not reference the producer execution callable type
    (``ExecutionOperation``), must not call a materialization session's
    ``add_record``/``add_logical_resource`` (only reads it), and must not
    dereference the opaque plan configuration.
    """
    assembly = (_ARTIFACTS_SRC / "assembly.py").read_text(encoding="utf-8")
    assert "ExecutionOperation" not in assembly
    assert "add_record" not in assembly
    assert "add_logical_resource" not in assembly
    assert "configuration[" not in assembly
    assert "configuration." not in assembly
