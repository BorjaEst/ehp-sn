"""Integration regression — Maze-ND is discoverable, plannable, and executable.

Since Phase 5.2 (Targets 1–14) the Maze-ND execution operation is registered in
``ehp_research`` against the generic execution composition. This proves:

* Target 5: execution availability and release selection are orthogonal;
* Target 14: removing the execution registration produces the controlled
  :class:`~ehp_sn.execution.MissingExecutionCapabilityError` (exit 6, no
  traceback) through the same generic path, and restoring it commits Maze-ND;
* Target 15: ``data build substrate:maze-nd/v1 --config <profile> --release 1``
  commits a durable release to an isolated artifact root containing unique
  normalized topology records, the complete source-lineage resource, and the
  standard manifest/config/provenance/index — and a second identical build
  reuses it without re-running extraction.

The remote source is deterministic and offline-testable: tests seed the Maze-ND
source loader with a bounded fixture population so the generic build → execution
→ materialization → publication lifecycle is exercised without network access.
The real ``--release 1`` publication against the authoritative HuggingFace
revision is the documented manual acceptance command.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from ehp_research.substrates import maze_nd
from ehp_research.substrates.maze_nd.source import content_fingerprint
from ehp_sn.cli import app
from ehp_sn.cli.data_adapter import DataOperationError, FrameworkDataAdapter
from ehp_sn.discovery import effective_registry
from ehp_sn.planning import effective_planning_composition
from typer.testing import CliRunner

#: Repo root, located relative to this test file (…/tests/integration/ → repo).
_REPO_ROOT = Path(__file__).resolve().parents[2]
_MAZE_ND_PROFILE = _REPO_ROOT / "config" / "data" / "maze-nd" / "reject-connected.toml"
_INTERIM_ROOT = _REPO_ROOT / "data" / "interim"
#: The coordinate that a successful --release 1 publication would occupy.
_MAZE_ND_V1 = _INTERIM_ROOT / "maze-nd" / "source-topology" / "v1"

runner = CliRunner()

WALL = "#"
OPEN = " "


def _grid(*rows: str) -> list[list[str]]:
    return [list(row) for row in rows]


def _labels_for(grid: list[list[str]]) -> list[list[str]]:
    return [[cell if cell in ("#", "S", "G") else " " for cell in row] for row in grid]


def _row(*rows: str) -> dict:
    grid = _grid(*rows)
    return {
        "inputs": grid,
        "labels": _labels_for(grid),
        "puzzle_index": 0,
        "group_index": 0,
        "set": "puzzle",
    }


def _fixture_rows():
    """A small bounded fixture population (train + test blobs + fingerprint)."""
    import gzip as _gzip

    train_rows = [
        _row("#S#", "#G#"),  # topology A
        _row("## ", "## "),  # topology B
    ]
    test_rows = [
        _row("#S#", "#G#"),  # topology A duplicate
        _row("##", "#S", "##"),  # topology C
    ]

    def _blob(rows):
        payload = "\n".join(json.dumps(r, separators=(",", ":")) for r in rows).encode("utf-8")
        return _gzip.compress(payload)

    train_blob = _blob(train_rows)
    test_blob = _blob(test_rows)
    return train_blob, test_blob, content_fingerprint(train_blob, test_blob)


def _seed_source_loader(monkeypatch) -> None:
    train_blob, test_blob, _fp = _fixture_rows()
    monkeypatch.setattr(
        maze_nd.execution,
        "load_source",
        lambda config, resource_source: maze_nd.source.iter_source_rows(
            config, resource_source, train_blob, test_blob
        ),
    )


def _adapter(tmp_path, *, execute=True):
    from ehp_research.registration import execution_registrations
    from ehp_sn.execution import SubstrateExecutionComposition

    composition = (
        SubstrateExecutionComposition(execution_registrations())
        if execute
        else SubstrateExecutionComposition(())
    )
    return FrameworkDataAdapter(
        effective_registry(),
        planning_composition=effective_planning_composition(),
        execution_composition=composition,
        root=tmp_path,
    )


def _fixture_profile(tmp_path, monkeypatch) -> str:
    """Write a Maze-ND profile whose fingerprint matches the fixture source.

    The repository profile declares the authoritative real-source fingerprint,
    which cannot match an injected fixture. This writes an equivalent
    ``source-topology`` profile carrying the fixture fingerprint so the generic
    build lifecycle is exercised offline and deterministically.
    """
    train_blob, test_blob, fingerprint = _fixture_rows()
    profile = tmp_path / "maze-nd-fixture.toml"
    profile.write_text(
        f"""[substrate]
    variant = "source-topology"

[source]
    reference              = "huggingface:flaitenberger/maze_hard_augmented"
    revision               = "rev-fixed"
    fingerprint            = "{fingerprint}"
    schema                 = "maze-nd:extraction/raster/v1"
    selection_policy       = "complete-source"
    selection_before_dedup = true

[normalization]
    policy = "maze-nd:normalization/raster/v1"

[topology]
    connectivity_policy  = "preserve"
    deduplication_policy = "maze-nd:dedup/orientation-preserving-raster/v1"
""",
        encoding="utf-8",
    )
    _seed_source_loader(monkeypatch)
    return str(profile)


def _tree(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {
        str(p.relative_to(path)): str(p.stat().st_size) for p in sorted(path.rglob("*")) if p.is_file()
    }


def test_maze_nd_is_registered_executable() -> None:
    """Maze-ND maps to a real execution operation by identity."""
    registry = effective_registry()
    definition = registry.resolve("substrate:maze-nd/v1")
    from ehp_research.registration import execution_registrations
    from ehp_sn.execution import SubstrateExecutionComposition

    composition = SubstrateExecutionComposition(execution_registrations())
    assert composition.contains(definition)
    assert composition.execute(definition) is maze_nd.execute


def test_python_maze_nd_build_commits_release(tmp_path, monkeypatch) -> None:
    """A ready plan with an execution capability commits a durable release."""
    from ehp_sn.artifacts import inspect_release, release_path
    from ehp_sn.planning import ReleaseCoordinate

    profile = _fixture_profile(tmp_path, monkeypatch)
    service = _adapter(tmp_path)
    outcome = service.build("substrate:maze-nd/v1", profile, release=1)

    assert outcome.action == "committed"
    assert outcome.target == "substrate:maze-nd/v1"
    assert outcome.output_contract == "raster-topology/v1"

    coordinate = ReleaseCoordinate(family="maze-nd", variant="source-topology", release=1)
    location = release_path(tmp_path, coordinate)
    assert inspect_release(tmp_path, coordinate).committed_exists is True

    # Standard committed resources.
    manifest = json.loads((location / "manifest.json").read_text(encoding="utf-8"))
    names = {r["name"] for r in manifest["resources"]}
    assert "resolved-config" in names
    assert "provenance" in names
    assert "index" in names
    assert "payloads" in names
    # The complete source-lineage is a committed auxiliary logical resource.
    assert "source-lineage" in names
    assert (location / "config.resolved.toml").exists()
    assert (location / "provenance.json").exists()
    assert (location / "index.jsonl").exists()
    assert (location / "resources" / "source-lineage.data").exists()

    # The committed index carries unique topology records.
    index_entries = [
        json.loads(line) for line in (location / "index.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(index_entries) == 3


def test_second_identical_build_reuses(tmp_path, monkeypatch) -> None:
    """A second identical build reuses the committed release (no re-extraction)."""

    profile = _fixture_profile(tmp_path, monkeypatch)
    adapter = _adapter(tmp_path)
    first = adapter.build("substrate:maze-nd/v1", profile, release=1)
    assert first.action == "committed"
    second = adapter.build("substrate:maze-nd/v1", profile, release=1)
    assert second.action == "reused"


def test_removing_registration_yields_controlled_missing_capability(tmp_path, monkeypatch) -> None:
    """Without the execution registration the generic path fails controlled (exit 6)."""
    profile = _fixture_profile(tmp_path, monkeypatch)
    adapter = _adapter(tmp_path, execute=False)
    with pytest.raises(DataOperationError) as exc:
        adapter.build("substrate:maze-nd/v1", profile, release=1)
    message = str(exc.value.message).lower()
    assert "execution" in message or "operation" in message


def test_cli_maze_nd_commit_isolated_root(tmp_path, monkeypatch) -> None:
    """The full accepted CLI command commits into the isolated root only."""
    from ehp_sn.cli import data as data_module

    profile = _fixture_profile(tmp_path, monkeypatch)
    data_module._set_adapter(_adapter(tmp_path))
    try:
        result = runner.invoke(
            app,
            [
                "data",
                "build",
                "substrate:maze-nd/v1",
                "--config",
                profile,
                "--release",
                "1",
            ],
        )
    finally:
        data_module._reset_adapter()

    assert result.exit_code == 0
    assert "Traceback" not in result.stderr
    # The CLI committed into the isolated root (maze-nd/source-topology/v1),
    # not into the repository's data/interim coordinate.
    isolated_release = tmp_path / "maze-nd" / "source-topology" / "v1"
    assert (isolated_release / "manifest.json").exists()
    assert _tree(isolated_release)
