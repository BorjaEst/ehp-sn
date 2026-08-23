"""CLI behavior tests for the ``ehp-sn data`` command group.

These tests focus almost entirely on CLI behavior (CLI-001): command existence,
argument and option interfaces, help text, delegation through the generic data
service seam, output formatting, failure formatting, and exit codes.

They run against a **fake** data service and never require real DungeonGen,
Maze-ND, or ObsField generation. A fake fifth substrate (``example-substrate/
v7``) is exercised to prove the CLI command logic is producer-neutral.
"""

from __future__ import annotations

from collections.abc import Sequence

import pytest
from ehp_sn.cli import app
from ehp_sn.cli import data as data_module
from ehp_sn.cli._data_service import (
    ArtifactNotFoundError,
    BuildResult,
    ConfigurationInvalidError,
    ConfigurationUnreadableError,
    DataNotImplementedError,
    DataOperationError,
    InspectResult,
    ListedSubstrate,
    PlanResult,
    ShowResult,
    UnknownSubstrateError,
    ValidateResult,
)
from ehp_sn.experiments import ComponentRef
from typer.testing import CliRunner

runner = CliRunner()


class _FakeTaskDefinition:
    """A non-substrate registered definition (task kind) for the wrong-kind test."""

    ref = ComponentRef.parse("task:synthetic/v1")

    @property
    def kind(self) -> str:
        return "task"


class FakeDataService:
    """In-memory fake backend implementing the ``DataService`` seam."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def _record(self, op: str, *args: object) -> None:
        self.calls.append((op, args))

    def list(self) -> Sequence[ListedSubstrate]:
        self._record("list")
        return (
            ListedSubstrate(ref="dagflow/v1", family="dagflow", output="simple-digraph/v1"),
            ListedSubstrate(ref="dungeongen/v1", family="dungeongen", output="raster-topology/v1"),
            ListedSubstrate(ref="maze-nd/v1", family="maze-nd", output="raster-topology/v1"),
            ListedSubstrate(ref="obsfield/v1", family="obsfield", output="categorical-field/v1"),
        )

    def show(self, target: str) -> ShowResult:
        self._record("show", target)
        if target == "example-substrate/v7":
            return ShowResult(ref=target, description="A fake fifth substrate.")
        raise UnknownSubstrateError(f"unknown substrate: {target}")

    def plan(self, target: str, config: str | None) -> PlanResult:
        self._record("plan", target, config)
        return PlanResult(target=target, config=config, status="planned")

    def build(self, target: str, config: str | None) -> BuildResult:
        self._record("build", target, config)
        return BuildResult(ref=target, action="created", location=f"data/interim/{target}")

    def validate(self, artifact: str, level: str) -> ValidateResult:
        self._record("validate", artifact, level)
        if artifact == "example-substrate/v7":
            return ValidateResult(artifact=artifact, ok=True)
        return ValidateResult(artifact=artifact, ok=False, errors=("manifest missing",), warnings=())

    def inspect(self, artifact: str, samples: int) -> InspectResult:
        self._record("inspect", artifact, samples)
        return InspectResult(
            artifact=artifact,
            summary={"kind": "raster-topology", "records": "10"},
            samples=(f"sample{i}" for i in range(samples)),
        )


@pytest.fixture()
def fake_service() -> FakeDataService:
    return FakeDataService()


@pytest.fixture()
def use_fake(fake_service: FakeDataService) -> FakeDataService:
    data_module._set_service(fake_service)
    yield fake_service
    data_module._reset_service()


# ---------------------------------------------------------------------------
# Command existence and help surface
# ---------------------------------------------------------------------------


def test_data_group_exists() -> None:
    result = runner.invoke(app, ["data", "--help"])
    assert result.exit_code == 0
    for command in ("list", "show", "plan", "build", "validate", "inspect"):
        assert command in result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["list"],
        ["show", "x"],
        ["plan", "x", "--config", "f.toml"],
        ["build", "x", "--config", "f.toml"],
        ["validate", "x"],
        ["inspect", "x"],
    ],
)
def test_each_command_help(args: list[str]) -> None:
    result = runner.invoke(app, ["data", *args, "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
    assert "Options" in result.stdout


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_list_renders_producer_summaries(use_fake: FakeDataService) -> None:
    result = runner.invoke(app, ["data", "list"])
    assert result.exit_code == 0
    assert "dagflow/v1" in result.stdout
    assert "maze-nd/v1" in result.stdout
    assert "obsfield/v1" in result.stdout
    assert "dungeongen/v1" in result.stdout


def test_list_json(use_fake: FakeDataService) -> None:
    result = runner.invoke(app, ["data", "list", "--format", "json"])
    assert result.exit_code == 0
    import json

    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["action"] == "list"
    assert len(payload["result"]) == 4


def test_list_delegates_to_service(use_fake: FakeDataService) -> None:
    runner.invoke(app, ["data", "list"])
    assert use_fake.calls == [("list", ())]


# ---------------------------------------------------------------------------
# show and producer neutrality
# ---------------------------------------------------------------------------


def test_show_delegates_and_renders(use_fake: FakeDataService) -> None:
    result = runner.invoke(app, ["data", "show", "example-substrate/v7"])
    assert result.exit_code == 0
    assert "Target: example-substrate/v7" in result.stdout
    assert use_fake.calls == [("show", ("example-substrate/v7",))]


def test_show_unknown_substrate_maps_to_exit_4(use_fake: FakeDataService) -> None:
    result = runner.invoke(app, ["data", "show", "no-such/v1"])
    assert result.exit_code == 4
    assert "unknown substrate" in result.stderr


# ---------------------------------------------------------------------------
# plan
# ---------------------------------------------------------------------------


def test_plan_requires_config() -> None:
    result = runner.invoke(app, ["data", "plan", "example-substrate/v7"])
    assert result.exit_code == 2
    assert "--config" in result.stdout or "--config" in result.stderr


def test_plan_delegates_config_path_opaquely(use_fake: FakeDataService) -> None:
    cfg = "config/data/example/family.toml"
    result = runner.invoke(app, ["data", "plan", "example-substrate/v7", "--config", cfg])
    assert result.exit_code == 0
    assert "target: example-substrate/v7" in result.stdout
    assert "config: config/data/example/family.toml" in result.stdout
    assert "status: planned" in result.stdout
    assert use_fake.calls == [("plan", ("example-substrate/v7", cfg))]


def test_plan_json(use_fake: FakeDataService) -> None:
    cfg = "config/data/example/other.toml"
    result = runner.invoke(
        app, ["data", "plan", "example-substrate/v7", "--config", cfg, "--format", "json"]
    )
    assert result.exit_code == 0
    import json

    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["action"] == "plan"
    assert payload["result"]["config"] == cfg


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


def test_build_requires_config() -> None:
    result = runner.invoke(app, ["data", "build", "example-substrate/v7"])
    assert result.exit_code == 2


def test_build_delegates_and_renders(use_fake: FakeDataService) -> None:
    cfg = "config/data/example/family.toml"
    result = runner.invoke(app, ["data", "build", "example-substrate/v7", "--config", cfg])
    assert result.exit_code == 0
    assert use_fake.calls == [("build", ("example-substrate/v7", cfg))]
    assert "created: example-substrate/v7" in result.stdout


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


def test_validate_ok_exit_0(use_fake: FakeDataService) -> None:
    result = runner.invoke(app, ["data", "validate", "example-substrate/v7"])
    assert result.exit_code == 0
    assert use_fake.calls == [("validate", ("example-substrate/v7", "full"))]


def test_validate_failure_exit_5(use_fake: FakeDataService) -> None:
    result = runner.invoke(app, ["data", "validate", "some-artifact"])
    assert result.exit_code == 5
    assert "FAIL: some-artifact" in result.stdout


def test_validate_level_passthrough(use_fake: FakeDataService) -> None:
    result = runner.invoke(app, ["data", "validate", "example-substrate/v7", "--level", "quick"])
    assert result.exit_code == 0
    assert use_fake.calls == [("validate", ("example-substrate/v7", "quick"))]


def test_validate_invalid_level_exit_2() -> None:
    result = runner.invoke(app, ["data", "validate", "x", "--level", "deep"])
    assert result.exit_code == 2


# ---------------------------------------------------------------------------
# inspect
# ---------------------------------------------------------------------------


def test_inspect_delegates_and_renders(use_fake: FakeDataService) -> None:
    result = runner.invoke(app, ["data", "inspect", "example-substrate/v7", "--samples", "2"])
    assert result.exit_code == 0
    assert use_fake.calls == [("inspect", ("example-substrate/v7", 2))]
    assert "Artifact: example-substrate/v7" in result.stdout
    assert "sample0" in result.stdout
    assert "sample1" in result.stdout


def test_inspect_negative_samples_exit_2() -> None:
    result = runner.invoke(app, ["data", "inspect", "x", "--samples", "-1"])
    assert result.exit_code == 2


# ---------------------------------------------------------------------------
# Controlled failure categories and exit codes
# ---------------------------------------------------------------------------


def test_default_backend_build_is_controlled_not_implemented() -> None:
    # No fake service: the production registry-backed backend is used, and an
    # unimplemented operation surfaces as a controlled message + exit 1, not a
    # traceback.
    data_module._reset_service()
    result = runner.invoke(app, ["data", "build", "substrate:dagflow/v1", "--config", "x.toml"])
    assert result.exit_code == 1
    assert "not yet implemented" in result.stderr
    assert "Traceback" not in result.stderr


def test_default_backend_plan_is_controlled_not_implied_success() -> None:
    # ``plan`` must no longer return a fake ``"planned"`` success; the real
    # backend reports it as not implemented.
    data_module._reset_service()
    result = runner.invoke(app, ["data", "plan", "substrate:dagflow/v1", "--config", "x.toml"])
    assert result.exit_code == 1
    assert "not yet implemented" in result.stderr
    assert "planned" not in result.stdout
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# Real registry-backed backend (production default, end to end)
# ---------------------------------------------------------------------------


def test_real_list_projects_installed_substrates() -> None:
    """The production default backend lists the installed Dagflow and Maze-ND defs."""
    try:
        import ehp_research  # noqa: F401
    except ImportError:  # pragma: no cover - skipping when not installed
        pytest.skip("ehp_research is not installed")

    data_module._reset_service()
    result = runner.invoke(app, ["data", "list"])
    assert result.exit_code == 0
    assert "substrate:dagflow/v1" in result.stdout
    assert "substrate:maze-nd/v1" in result.stdout
    assert "simple-digraph/v1" in result.stdout
    assert "raster-topology/v1" in result.stdout


def test_real_show_projects_the_installed_definition() -> None:
    try:
        import ehp_research  # noqa: F401
    except ImportError:  # pragma: no cover - skipping when not installed
        pytest.skip("ehp_research is not installed")

    data_module._reset_service()
    result = runner.invoke(app, ["data", "show", "substrate:dagflow/v1"])
    assert result.exit_code == 0
    assert "Target: substrate:dagflow/v1" in result.stdout
    assert "Description:" in result.stdout


def test_real_show_unknown_substrate_is_controlled_exit_4() -> None:
    try:
        import ehp_research  # noqa: F401
    except ImportError:  # pragma: no cover - skipping when not installed
        pytest.skip("ehp_research is not installed")

    data_module._reset_service()
    result = runner.invoke(app, ["data", "show", "substrate:not-registered/v1"])
    assert result.exit_code == 4
    assert "unknown substrate" in result.stderr
    assert "Traceback" not in result.stderr


def test_real_show_wrong_kind_is_controlled() -> None:
    """A reference that exists but is not a substrate must not succeed in ``show``."""
    try:
        import ehp_research  # noqa: F401
    except ImportError:  # pragma: no cover - skipping when not installed
        pytest.skip("ehp_research is not installed")

    # Give the effective registry a registered task reference in isolation.
    from ehp_research.registration import register_components
    from ehp_sn.discovery import ComponentRegistry

    registry = ComponentRegistry()
    register_components(registry)
    registry.register(_FakeTaskDefinition())
    from ehp_sn.cli.data_adapter import FrameworkDataService

    data_module._set_service(FrameworkDataService(registry))
    result = runner.invoke(app, ["data", "show", "task:synthetic/v1"])
    data_module._reset_service()
    assert result.exit_code == 4
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    ("exc", "expected_code", "expected_text"),
    [
        (UnknownSubstrateError("no such substrate"), 4, "no such substrate"),
        (ConfigurationUnreadableError("cannot read config"), 4, "cannot read config"),
        (ConfigurationInvalidError("bad schema"), 3, "bad schema"),
        (ArtifactNotFoundError("artifact missing"), 4, "artifact missing"),
        (DataOperationError("generation failed"), 6, "generation failed"),
        (DataNotImplementedError("not implemented"), 1, "not implemented"),
    ],
)
def test_error_categories_map_to_exit_codes(
    exc: Exception, expected_code: int, expected_text: str
) -> None:
    class RaisingService:
        def list(self):
            raise exc

        def show(self, target):
            raise exc

        def plan(self, target, config):
            raise exc

        def build(self, target, config):
            raise exc

        def validate(self, artifact, level):
            raise exc

        def inspect(self, artifact, samples):
            raise exc

    data_module._set_service(RaisingService())
    result = runner.invoke(app, ["data", "build", "example-substrate/v7", "--config", "x.toml"])
    data_module._reset_service()
    assert result.exit_code == expected_code
    assert expected_text in result.stderr
    assert "Traceback" not in result.stderr


def test_bare_not_implemented_is_controlled() -> None:
    class RaisingService:
        def build(self, target, config):
            raise NotImplementedError

    data_module._set_service(RaisingService())  # type: ignore[arg-type]
    result = runner.invoke(app, ["data", "build", "x", "--config", "y.toml"])
    data_module._reset_service()
    assert result.exit_code == 1
    assert "not yet implemented" in result.stderr
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# Producer neutrality
# ---------------------------------------------------------------------------


def test_cli_source_has_no_producer_conditionals() -> None:
    """The CLI module must not name producer families or branch on them."""
    import inspect as _inspect

    source = _inspect.getsource(data_module)
    for producer in ("dagflow", "dungeongen", "maze-nd", "obsfield"):
        assert producer not in source.lower()
