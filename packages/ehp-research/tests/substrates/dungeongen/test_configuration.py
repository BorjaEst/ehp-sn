"""DungeonGen configuration resolution tests.

Verifies the frozen dependency identity, the supported parameter contract with
EHP-owned defaults and the size/room_count mutual exclusion, the
acceptance/duplicate/size policies, and the clean rejection of the
valid-but-unimplemented ``reject-exact`` duplicate policy.
"""

from __future__ import annotations

import pytest
from ehp_research.substrates import dungeongen
from ehp_research.substrates.dungeongen._dependency import (
    ACCEPTANCE_POLICY,
    DEPENDENCY_REFERENCE,
    PROFILE_REFERENCE,
    PROTOCOL_REFERENCE,
    UPSTREAM_REVISION,
)
from ehp_research.substrates.dungeongen.configuration import (
    DungeonGenConfigurationError,
    resolve_configuration,
)

from ._fixtures import DEFAULT_PARAMS, config_document, loaded_document


def test_dependency_identity_is_frozen_at_upstream_revision() -> None:
    """The exact Git commit is frozen, not a mutable package name."""
    assert UPSTREAM_REVISION == "2d228f5d3f82ccaa4666b087942100e7800fb069"
    assert DEPENDENCY_REFERENCE.endswith(UPSTREAM_REVISION)
    assert dungeongen.DEPENDENCY_REFERENCE == DEPENDENCY_REFERENCE


def test_resolve_complete_first_profile() -> None:
    """A complete resolved profile yields a complete explicit GenerationParams.

    Every supported field is present on the resolved declaration; no field
    silently inherits an upstream default.
    """
    cfg = resolve_configuration(loaded_document())
    assert cfg.variant == "general"
    assert cfg.generator_dependency == DEPENDENCY_REFERENCE
    assert cfg.generator_protocol == PROTOCOL_REFERENCE
    assert cfg.generator_profile == PROFILE_REFERENCE
    assert cfg.conversion_policy == "dungeongen:conversion/raster/v1"
    assert cfg.component_selection_policy == "dungeongen:selection/largest-component/v1"
    assert cfg.acceptance_policy == ACCEPTANCE_POLICY
    assert cfg.duplicate_policy == "allow"
    assert cfg.randomness_role == "topology-candidate"
    # Every default param field is reflected explicitly on the resolved profile.
    assert cfg.profile.archetype == DEFAULT_PARAMS["archetype"]
    assert cfg.profile.size == DEFAULT_PARAMS["size"]
    assert cfg.profile.passage_width == DEFAULT_PARAMS["passage_width"]
    assert cfg.profile.water_enabled is False
    # room_count is optional and absent -> the explicit "derive from size" state.
    assert cfg.profile.room_count is None


def test_omitted_params_resolve_via_ehp_owned_defaults() -> None:
    """An omitted field resolves through the EHP-owned default.

    The user configuration may supply only a subset; EHP-owned defaults fill the
    remainder so the resolved declaration is complete and explicit. The generated
    distribution is not frozen: only the default for an omitted field is EHP-owned.
    """
    # A minimal config that sets none of the scientific generator parameters.
    cfg = resolve_configuration(loaded_document(params={}))
    assert cfg.profile.density == 0.5  # EHP-owned default
    assert cfg.profile.archetype == "classic"
    assert cfg.profile.size == "medium"
    assert cfg.profile.loop_factor == 0.3
    assert cfg.profile.levels == 1

    # A config that overrides a single field keeps EHP defaults for the rest.
    cfg2 = resolve_configuration(loaded_document(params={"density": 0.8}))
    assert cfg2.profile.density == 0.8
    assert cfg2.profile.archetype == "classic"  # EHP default for the omitted field
    assert cfg2.profile.size == "medium"


def test_changing_scientific_params_changes_identity() -> None:
    """A parameter change alters the build-input identity."""
    from ehp_research.substrates.dungeongen.configuration import profile_identity_values

    base = resolve_configuration(loaded_document())
    denser = resolve_configuration(loaded_document(params={"density": 0.6}))
    assert profile_identity_values(base.profile) != profile_identity_values(denser.profile)
    loopy = resolve_configuration(loaded_document(params={"loop_factor": 0.5}))
    assert profile_identity_values(base.profile) != profile_identity_values(loopy.profile)


def test_profile_rejects_unknown_params() -> None:
    params = dict(DEFAULT_PARAMS)
    params["not_a_real_option"] = 1
    with pytest.raises(DungeonGenConfigurationError):
        resolve_configuration(loaded_document(params=params))


def test_profile_rejects_bad_enum_and_range() -> None:
    with pytest.raises(DungeonGenConfigurationError):
        resolve_configuration(loaded_document(params={**DEFAULT_PARAMS, "size": "gigantic"}))
    with pytest.raises(DungeonGenConfigurationError):
        resolve_configuration(loaded_document(params={**DEFAULT_PARAMS, "density": 2.0}))


def test_room_count_size_mutual_exclusion() -> None:
    """Size and room_count are mutually exclusive."""
    # size only is valid; room_count derives from size (upstream-owned).
    cfg = resolve_configuration(loaded_document(params={"size": "large"}))
    assert cfg.profile.size == "large"
    assert cfg.profile.room_count is None

    # room_count only is valid and wins over size.
    cfg2 = resolve_configuration(loaded_document(params={"room_count": [6, 10]}))
    assert cfg2.profile.room_count == (6, 10)

    # both set -> conflict.
    with pytest.raises(DungeonGenConfigurationError) as exc:
        resolve_configuration(loaded_document(params={"size": "large", "room_count": [6, 10]}))
    assert "room_count" in str(exc.value)

    # invalid room_count form.
    with pytest.raises(DungeonGenConfigurationError):
        resolve_configuration(loaded_document(params={"room_count": [10, 6]}))
    with pytest.raises(DungeonGenConfigurationError):
        resolve_configuration(loaded_document(params={"room_count": [0, 6]}))


def test_room_count_is_identity_bearing_when_set() -> None:
    """An explicit room_count alters identity; a None room_count does not."""
    from ehp_research.substrates.dungeongen.configuration import profile_identity_values

    base = resolve_configuration(loaded_document())
    with_room_count = resolve_configuration(loaded_document(params={"room_count": [6, 10]}))
    # A set room_count must change identity.
    assert profile_identity_values(base.profile) != profile_identity_values(with_room_count.profile)
    # A None room_count + size derives from size exactly as the default profile,
    # so it is not identity-bearing beyond the size already encoded.
    by_size = resolve_configuration(loaded_document(params={"size": "medium"}))
    assert profile_identity_values(base.profile) == profile_identity_values(by_size.profile)


def test_reject_invalid_dependency() -> None:
    """A non-frozen dependency reference is rejected."""
    doc = config_document()
    doc["generator"]["dependency"] = "pip install dungeongen@main"
    from pathlib import Path

    from ehp_sn.configuration import LoadedConfiguration

    cfg = LoadedConfiguration(source=Path("<x>"), values=doc)
    with pytest.raises(DungeonGenConfigurationError):
        resolve_configuration(cfg)


def test_reject_exact_is_rejected_cleanly() -> None:
    """Reject-exact is valid but unsupported; rejected, not downgraded."""
    with pytest.raises(DungeonGenConfigurationError) as exc:
        resolve_configuration(loaded_document(duplicate_policy="reject-exact"))
    assert "reject-exact" in str(exc.value)
    assert "allow" in str(exc.value)


def test_allow_is_supported() -> None:
    cfg = resolve_configuration(loaded_document(duplicate_policy="allow"))
    assert cfg.duplicate_policy == "allow"


def test_region_policy_absent_by_default() -> None:
    """No region policy is present in the first implementation."""
    cfg = resolve_configuration(loaded_document())
    assert not hasattr(cfg, "region_policy")


def test_size_policy_resolved() -> None:
    cfg = resolve_configuration(loaded_document())
    assert cfg.size_policy.minimum_states == 4
    assert cfg.size_policy.maximum_states == 100
    assert cfg.size_policy.minimum_height == 2
