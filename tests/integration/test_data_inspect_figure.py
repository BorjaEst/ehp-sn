"""Integration tests — Phase 1 ``data inspect --figure`` over real committed artifacts.

This is the root-level integration scope for the Phase-1 figure walking skeleton.
It proves the complete production path end to end over **real committed
artifacts** and the real CLI: an exact ``data inspect ARTIFACT --record RECORD_ID
--figure FIGURE_REF`` request resolves through the ordinary figure catalogue,
validates, projects with exact provenance, and realizes a Matplotlib Figure.

These are integration tests because they depend on committed artifacts under
``data/interim`` that are produced by real research providers; unit-level figure
behaviour lives in ``packages/ehp-sn/tests/figures/``.

They run headlessly (non-interactive Matplotlib backend) with no X11/Wayland/
desktop/GUI event loop (Phase-1 § 16 · P1-T14, § 19.11).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend required for P1-19.11

import pytest
from ehp_sn.cli import app
from typer.testing import CliRunner

#: Repo root, located relative to this test file (…/tests/integration/ → repo).
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DUNGEONGEN_RASTER = _REPO_ROOT / "data" / "interim" / "dungeongen" / "general" / "v1"
_DAGFLOW_DIGRAPH = _REPO_ROOT / "data" / "interim" / "dagflow" / "single-terminal" / "v1"

_FIGURE_REF = "figure:raster-topology-inspection/v1"

runner = CliRunner()


def _first_record_id(artifact_dir: Path) -> str:
    with open(artifact_dir / "index.jsonl", encoding="utf-8") as handle:
        first = json.loads(handle.readline())
    return first["record_id"]


# ---------------------------------------------------------------------------
# 19.1 a real committed raster record realizes through the ordinary figure path
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _DUNGEONGEN_RASTER.is_dir(),
    reason="committed DungeonGen raster artifact is not present",
)
def test_inspect_figure_success_headless() -> None:
    """``data inspect --figure`` over a committed raster record succeeds headlessly (exit 0)."""
    record_id = _first_record_id(_DUNGEONGEN_RASTER)
    result = runner.invoke(
        app,
        [
            "data",
            "inspect",
            str(_DUNGEONGEN_RASTER),
            "--record",
            record_id,
            "--figure",
            _FIGURE_REF,
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["action"] == "inspect"
    assert payload["result"]["schema_ref"] == "raster-topology/v1"
    assert payload["result"]["figure"] == _FIGURE_REF
    assert payload["result"]["projection_identity"].startswith("sha256:")


# ---------------------------------------------------------------------------
# 19.2 unknown figure → controlled exit without a traceback
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _DUNGEONGEN_RASTER.is_dir(),
    reason="committed DungeonGen raster artifact is not present",
)
def test_inspect_figure_unknown_figure_exit_4() -> None:
    """An unknown figure reference is a controlled catalogue error (exit 4)."""
    record_id = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
    result = runner.invoke(
        app,
        [
            "data",
            "inspect",
            str(_DUNGEONGEN_RASTER),
            "--record",
            record_id,
            "--figure",
            "figure:does-not-exist/v1",
        ],
    )
    # The figure resolution fails before record resolution matters; both are
    # controlled and exit 4 (unknown figure) / not a traceback.
    assert result.exit_code in (4, 6)
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# 19.3 contract mismatch → controlled exit 3 before rendering
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _DAGFLOW_DIGRAPH.is_dir(),
    reason="committed Dagflow simple-digraph artifact is not present",
)
def test_inspect_figure_contract_mismatch_exit_3() -> None:
    """Requesting the raster figure over a simple-digraph record is exit 3 (input incompatible)."""
    record_id = _first_record_id(_DAGFLOW_DIGRAPH)
    result = runner.invoke(
        app,
        [
            "data",
            "inspect",
            str(_DAGFLOW_DIGRAPH),
            "--record",
            record_id,
            "--figure",
            _FIGURE_REF,
        ],
    )
    assert result.exit_code == 3
    assert "requires source role 'topology'" in result.stderr
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# 19.1 Python-API level: the figure service projects a committed record directly
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _DUNGEONGEN_RASTER.is_dir(),
    reason="committed DungeonGen raster artifact is not present",
)
def test_inspect_figure_service_projects_committed_record() -> None:
    """``ehp_sn.figures.inspect_figure`` projects a committed raster record directly.

    Same real committed artifact and figure path as the CLI test, but exercised
    through the framework Python figure service (the same orchestration the CLI
    delegates to), proving the Python and CLI surfaces converge on the same
    projection semantics (CONFIG-004 figure slice).
    """
    from ehp_sn.figures import inspect_figure

    record_id = _first_record_id(_DUNGEONGEN_RASTER)
    result = inspect_figure(
        str(_DUNGEONGEN_RASTER),
        record_id,
        _FIGURE_REF,
        artifact_root=_REPO_ROOT / "data" / "interim",
    )
    projection = result.projection
    assert projection.source.logical_contract == "raster-topology/v1"
    assert projection.source.record_id == record_id
    assert projection.figure_ref == _FIGURE_REF
    assert type(result.figure).__name__ == "Figure"
    assert len(result.figure.axes) == 1
