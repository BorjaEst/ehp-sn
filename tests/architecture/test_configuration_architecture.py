"""Architecture invariants for Phase 3B Capability 4 — generic configuration.

These tests enforce that the generic configuration layer
(``ehp_sn.configuration``) stays a generic, framework-owned configuration
input boundary:

* it must not import ``ehp_research`` (ARCH-001 direction);
* it must contain no substrate-family names (Dagflow / Maze-ND) and no
  substrate-family dispatch;
* it must not depend on ``ehp_sn.cli`` (no exit-code / interface semantics) or
  ``ehp_sn.discovery`` (the configuration loader does not need discovery to
  parse a file).

These are source-level structural checks, independent of runtime behavior.
Semantic configuration resolution is owned downstream by research producers
(Capability 5) and is intentionally out of scope for this package.
"""

from __future__ import annotations

import pathlib

import pytest

#: Source roots of the two packages, discovered relative to this file.
_PACKAGES_ROOT = pathlib.Path(__file__).resolve().parents[2] / "packages"
_EHP_SN_SRC = _PACKAGES_ROOT / "ehp-sn" / "src" / "ehp_sn"
_CONFIGURATION_SRC = _EHP_SN_SRC / "configuration"


def _py_files(root: pathlib.Path) -> list[pathlib.Path]:
    return [p for p in root.rglob("*.py") if p.is_file()]


def _import_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.lstrip().startswith(("import ", "from "))]


def test_configuration_never_imports_ehp_research() -> None:
    """The framework configuration layer must not depend on ehp_research."""
    offenders: list[str] = []
    for file in _py_files(_CONFIGURATION_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        if any("ehp_research" in line for line in import_lines):
            offenders.append(str(file))
    assert offenders == [], f"ehp_sn.configuration must not import ehp_research; found in: {offenders}"


def test_configuration_has_no_substrate_family_names() -> None:
    """The configuration layer must not know Dagflow or Maze-ND."""
    for file in _py_files(_CONFIGURATION_SRC):
        text = file.read_text(encoding="utf-8")
        assert "dagflow" not in text.lower(), file
        assert "maze-nd" not in text.lower(), file
        assert "maze_nd" not in text.lower(), file


def test_configuration_does_not_depend_on_cli_or_discovery() -> None:
    """The loader needs no interface or discovery machinery to parse a file."""
    forbidden_import_targets = ("ehp_sn.cli", "ehp_sn.discovery")
    offenders: list[str] = []
    for file in _py_files(_CONFIGURATION_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        for line in import_lines:
            if any(target in line for target in forbidden_import_targets):
                offenders.append(f"{file}: {line.strip()}")
    assert offenders == [], (
        f"ehp_sn.configuration must not depend on ehp_sn.cli or ehp_sn.discovery; found: {offenders}"
    )
