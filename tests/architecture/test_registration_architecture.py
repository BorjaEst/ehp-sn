"""Architecture invariants for Phase 3A Capability 2 — provider registration.

These tests enforce the package-boundary invariant documented by both package
READMEs and ``docs/invariants.md`` (ARCH-001/ARCH-003):

    ehp_research → ehp_sn
    ehp_sn       ↛ ehp_research   (forbidden)

The research registration integration (:func:`ehp_research.registration
.register_components`) consumes the generic framework boundary; the framework
must remain independent of concrete research packages and must not branch on
any substrate family. These are source-level structural checks, independent of
runtime behavior.
"""

from __future__ import annotations

import pathlib

import pytest

#: Source roots of the two packages, discovered relative to this file.
_PACKAGES_ROOT = pathlib.Path(__file__).resolve().parents[2] / "packages"
_EHP_SN_SRC = _PACKAGES_ROOT / "ehp-sn" / "src" / "ehp_sn"
_EHP_RESEARCH_SRC = _PACKAGES_ROOT / "ehp-research" / "src" / "ehp_research"


def _py_files(root: pathlib.Path) -> list[pathlib.Path]:
    return [p for p in root.rglob("*.py") if p.is_file()]


def _import_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.lstrip().startswith(("import ", "from "))]


def test_ehp_sn_discovers_generically_without_family_branching() -> None:
    """Capability 2 must require zero special handling in ``ehp_sn``.

    The discovery package must contain no substrate-family token, so the
    framework never special-cases Dagflow or Maze-ND.
    """
    discovery_src = _EHP_SN_SRC / "discovery"
    assert discovery_src.is_dir(), "expected ehp_sn.discovery source package"

    for file in _py_files(discovery_src):
        text = file.read_text(encoding="utf-8").lower()
        assert "dagflow" not in text, file
        assert "maze-nd" not in text, file


@pytest.mark.parametrize(
    "family_name",
    ["dagflow", "maze_nd"],
)
def test_ehp_research_substrate_definition_imports_only_framework(
    family_name: str,
) -> None:
    """Each research definition's home may depend only on framework discovery."""
    # Ignore the standard ``from __future__ import annotations`` line: it is a
    # language-version directive, not a dependency import.
    import_lines = [
        line
        for line in _import_lines(
            (_EHP_RESEARCH_SRC / "substrates" / family_name / "definition.py").read_text(
                encoding="utf-8"
            )
        )
        if "__future__" not in line
    ]
    assert import_lines, "expected at least one dependency import in the definition module"
    for line in import_lines:
        assert "ehp_research" not in line
        assert "ehp_sn" in line or ".." in line, line
