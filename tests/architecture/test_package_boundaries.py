"""Repository-level package boundary invariants.

This file is the authoritative home for the general dependency-direction
invariant across packages (documented in ``docs/invariants.md`` ARCH-001/ARCH-003
and both package READMEs):

    ehp_research → ehp_sn
    ehp_sn       ↛ ehp_research   (forbidden)

Capability-specific structural checks (registration family-branching,
configuration independence, definition-module autonomy) live beside their
capability tests; this file owns the *package-to-package* direction only.
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


def test_ehp_sn_never_imports_ehp_research() -> None:
    """The framework must never depend on a concrete research package (ARCH-001)."""
    offenders: list[str] = []
    for file in _py_files(_EHP_SN_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        if any("ehp_research" in line for line in import_lines):
            offenders.append(str(file))
    assert offenders == [], (
        f"ehp_sn must not import ehp_research; found forbidden imports in: {offenders}"
    )


def test_ehp_research_may_depend_on_ehp_sn() -> None:
    """The allowed direction (``ehp_research → ehp_sn``) is actually exercised.

    At least one research source module must reference the framework so the
    dependency is real, not merely permitted.
    """
    referencing: list[str] = []
    for file in _py_files(_EHP_RESEARCH_SRC):
        import_lines = _import_lines(file.read_text(encoding="utf-8"))
        if any("ehp_sn" in line for line in import_lines):
            referencing.append(str(file))
    assert referencing, "expected ehp_research to depend on ehp_sn"


def test_ehp_sn_has_single_discovery_authority() -> None:
    """The framework must not hard-code provider packages or their entry points.

    ``ehp_sn`` declares one generic provider entry-point group and composes
    installed providers generically; it must not name any concrete research
    package or entry-point function, which would duplicate the registration
    authority that belongs to the downstream package.
    """
    from ehp_sn.discovery import providers as providers_module

    group = providers_module.PROVIDER_ENTRY_POINT_GROUP
    assert group == "ehp_sn.providers"
    assert "ehp_research" not in group

    # Compose via the generic mechanism but never import a provider by name.
    source = providers_module.__file__
    text = pathlib.Path(source).read_text(encoding="utf-8")
    import_lines = [line for line in text.splitlines() if line.lstrip().startswith(("import ", "from "))]
    assert not any("ehp_research" in line for line in import_lines)
