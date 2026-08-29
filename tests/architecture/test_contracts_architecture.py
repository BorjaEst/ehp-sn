"""Architecture invariants for the framework-owned shared contracts package.

These tests enforce that ``ehp_sn.contracts`` stays framework-owned and generic:

* it must not import ``ehp_research`` (ARCH-001 direction) nor ``ehp_sn.cli``
  (no exit-code / interface semantics);
* it must contain no substrate-family names (Dagflow / ObsField / Maze-ND /
  DungeonGen), so contracts never know who produces or consumes them.

A contract here must remain meaningful if ``ehp_research`` did not exist.
"""

from __future__ import annotations

import pathlib
import re

_PACKAGES_ROOT = pathlib.Path(__file__).resolve().parents[2] / "packages"
_EHP_SN_SRC = _PACKAGES_ROOT / "ehp-sn" / "src" / "ehp_sn"
_CONTRACTS_SRC = _EHP_SN_SRC / "contracts"

_FAMILY_TOKENS = ("dagflow", "obsfield", "maze-nd", "maze_nd", "dungeongen")


def _py_files(root: pathlib.Path) -> list[pathlib.Path]:
    return [p for p in root.rglob("*.py") if p.is_file()]


def _import_lines(text: str) -> list[str]:
    """Return only genuine import statements (not docstring prose)."""
    return [
        line
        for line in text.splitlines()
        if re.match(r"^\s*(from\s+\.?[A-Za-z_][\w\.]*\s+import|import\s+\.?[A-Za-z_][\w\.]*)", line)
    ]


def test_contracts_never_imports_ehp_research() -> None:
    """The shared contracts must not depend on a concrete research package."""
    offenders: list[str] = []
    for file in _py_files(_CONTRACTS_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        if any("ehp_research" in line for line in import_lines):
            offenders.append(str(file))
    assert offenders == [], f"ehp_sn.contracts must not import ehp_research; found in: {offenders}"


def test_contracts_does_not_depend_on_cli() -> None:
    """Contracts carry no exit-code / interface semantics."""
    offenders: list[str] = []
    for file in _py_files(_CONTRACTS_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        for line in import_lines:
            if "ehp_sn.cli" in line:
                offenders.append(f"{file}: {line.strip()}")
    assert offenders == [], f"ehp_sn.contracts must not depend on ehp_sn.cli; found: {offenders}"


def test_contracts_has_no_substrate_family_names() -> None:
    """The shared contracts must not know Dagflow, ObsField, Maze-ND, or DungeonGen."""
    for file in _py_files(_CONTRACTS_SRC):
        text = file.read_text(encoding="utf-8").lower()
        for token in _FAMILY_TOKENS:
            assert token not in text, f"{file} must not contain family token {token!r}"


def test_contracts_imports_only_framework_or_stdlib() -> None:
    """Contracts depend only on the standard library (self-contained semantics)."""
    for file in _py_files(_CONTRACTS_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        for line in import_lines:
            parts = line.split()
            if not parts or parts[0] == "from" and len(parts) < 2:
                continue
            module = parts[1]
            if module == "__future__":
                continue
            # Relative imports stay inside the framework contracts package.
            if module.startswith("."):
                continue
            top = module.split(".")[0]
            assert top in ("ehp_sn", "typing", "collections", "dataclasses", "abc"), (
                f"{file} imports non-framework/non-stdlib module: {module}"
            )
