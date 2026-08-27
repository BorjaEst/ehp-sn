"""Authoritative DungeonGen v1 producer-owned configuration resolution.

This module is the single authoritative home for turning the generic
configuration document produced by the framework configuration loader
(``ehp_sn.configuration.load_configuration``) into the immutable, fully
effective DungeonGen scientific configuration.

It owns only DungeonGen semantics. It interprets a generic parsed document
(:class:`~ehp_sn.configuration.LoadedConfiguration`) as a valid DungeonGen
configuration — nothing more. The concrete pipeline it implements is::

    generic parsed configuration
            ↓
    dungeongen.resolve_configuration(document)
            ↓
    DungeonGenConfiguration (immutable, fully effective)

It deliberately does **not**:

* load files, download, or inspect the external generator;
* invoke the upstream generator or run candidate retries;
* compute build-input identities, fingerprints, or digests;
* plan, convert, normalize, accept, or execute the producer;
* translate to a CLI-facing error (no exit-code semantics).

The resolver freezes the exact external dependency identity, the
reference protocol and the supported parameter contract (Corrections 2 and 3),
and every producer-owned acceptance/duplicate policy. It resolves the complete
effective generator parameter declaration by applying EHP-owned defaults
to whatever the user configuration supplies, and enforces the
optional/mutual-exclusion semantics of ``size`` vs ``room_count``. It
carries the dependency requirement as declared scientific state; it does not
verify the installed package (that is a BUILD-readiness concern enforced at
execution time from the frozen identity).

No field is invented beyond the authoritative specification
``docs/docs/research/substrates/dungeongen-v1.md`` and the reusable repository
profiles under ``config/data/dungeongen/``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

from ehp_sn.configuration import LoadedConfiguration

from ._dependency import (
    ACCEPTANCE_POLICY,
    COMPONENT_SELECTION_POLICY,
    CONVERSION_POLICY,
    DEPENDENCY_REFERENCE,
    PROFILE_REFERENCE,
    PROTOCOL_REFERENCE,
    RANDOMNESS_ROLE,
)

#: The only valid ``general`` variant for dungeongen/v1.
VALID_VARIANT: Final = "general"

#: Valid duplicate policies.
VALID_DUPLICATE_POLICIES: Final = ("allow", "reject-exact")

#: The first executable profile implements ``allow`` only. A config
#: declaring ``reject-exact`` is rejected cleanly until that policy is
#: implemented and registered; it must never be silently downgraded to ``allow``.
SUPPORTED_DUPLICATE_POLICIES: Final = ("allow",)

#: Valid ``GenerationParams`` enum values (mirror the frozen upstream 0.1.14).
VALID_ARCHETYPES: Final = ("classic", "warren", "temple", "crypt", "cavern", "fortress", "lair")
VALID_SIZES: Final = ("tiny", "small", "medium", "large", "xlarge")
VALID_SYMMETRIES: Final = ("none", "bilateral", "radial_2", "radial_4", "partial")

_REQUIRED_TOP_LEVEL_TABLES: Final = (
    "substrate",
    "generator",
    "conversion",
    "acceptance",
    "generation",
    "topology",
)

#: Accepted producer keys per table.
_ACCEPTED_SUBSTRATE_KEYS: Final = ("variant",)
_ACCEPTED_GENERATOR_KEYS: Final = ("dependency", "protocol", "profile", "params")
_ACCEPTED_CONVERSION_KEYS: Final = ("policy",)
_ACCEPTED_ACCEPTANCE_KEYS: Final = ("policy", "require_connected")
_ACCEPTED_GENERATION_KEYS: Final = ("attempt_budget", "seed", "record_count", "role")
_ACCEPTED_TOPOLOGY_KEYS: Final = ("duplicate_policy", "size_policy")
_ACCEPTED_SIZE_POLICY_KEYS: Final = (
    "minimum_height",
    "maximum_height",
    "minimum_width",
    "maximum_width",
    "minimum_states",
    "maximum_states",
)

# Supported parameters
SUPPORTED_PARAM_FIELDS: Final = (
    "archetype",
    "size",
    "room_count",
    "room_size_bias",
    "round_room_chance",
    "hall_chance",
    "density",
    "symmetry",
    "symmetry_break",
    "linearity",
    "loop_factor",
    "passage_width",
    "winding",
    "extra_room_connections",
    "extra_passage_junctions",
    "levels",
    "stair_frequency",
    "water_enabled",
    "water_threshold",
)

_EHP_PARAM_DEFAULTS: Final = {
    "archetype": "classic",
    "size": "medium",
    "room_size_bias": 0.0,
    "round_room_chance": 0.15,
    "hall_chance": 0.1,
    "density": 0.5,
    "symmetry": "none",
    "symmetry_break": 0.2,
    "linearity": 0.3,
    "loop_factor": 0.3,
    "passage_width": 1,
    "winding": 0.0,
    "extra_room_connections": 0.2,
    "extra_passage_junctions": 0.15,
    "levels": 1,
    "stair_frequency": 0.1,
    "water_enabled": False,
    "water_threshold": 0.15,
}


class DungeonGenConfigurationError(ValueError):
    """A loaded configuration is not a valid DungeonGen v1 configuration.

    Raised by :func:`resolve_configuration` when the generic configuration
    document violates a DungeonGen scientific invariant: a required field is
    missing, an unrecognized producer key is present, an invalid enum value is
    supplied, a frozen parameter field is omitted, or a currently unsupported
    (but valid) scientific choice such as ``reject-exact`` is requested. It is
    a DungeonGen-owned semantic error, not a framework loading or CLI error.
    """


@dataclass(frozen=True, slots=True)
class GeneratorProfile:
    """The resolved, complete, and fully explicit generator parameter declaration.

    Holds the complete effective ``GenerationParams`` surface after applying
    EHP-owned defaults to whatever the user configuration supplied.
    Every EHP-defaulted field is present with an explicit value, so the
    upstream generator defaults are never silently inherited.

    ``room_count`` is optional and mutually exclusive with ``size``:
    ``None`` is the explicit "derive room count from size" state ;
    a tuple is an explicit override that wins over ``size``.
    """

    archetype: str
    size: str
    room_count: tuple[int, int] | None
    room_size_bias: float
    round_room_chance: float
    hall_chance: float
    density: float
    symmetry: str
    symmetry_break: float
    linearity: float
    loop_factor: float
    passage_width: int
    winding: float
    extra_room_connections: float
    extra_passage_junctions: float
    levels: int
    stair_frequency: float
    water_enabled: bool
    water_threshold: float


@dataclass(frozen=True, slots=True)
class SizePolicy:
    """Declared allowed extent and state-count bounds."""

    minimum_height: int
    maximum_height: int
    minimum_width: int
    maximum_width: int
    minimum_states: int
    maximum_states: int


@dataclass(frozen=True, slots=True)
class DungeonGenConfiguration:
    """Immutable, fully effective DungeonGen v1 scientific configuration.

    ``variant`` is always the validated ``general`` value. The generator
    identity fields (``generator_dependency``, ``protocol``, ``profile``) freeze
    the external dependency and EHP-SN reference protocol/profile. ``profile``
    holds the fully explicit generator parameter profile; ``seed``,
    ``record_count``, and ``attempt_budget`` drive deterministic candidate
    generation; ``duplicate_policy`` is ``allow`` for the first release.
    """

    variant: str
    generator_dependency: str
    generator_protocol: str
    generator_profile: str
    profile: GeneratorProfile
    conversion_policy: str
    component_selection_policy: str
    acceptance_policy: str
    require_connected: bool
    randomness_role: str
    seed: int
    record_count: int
    attempt_budget: int
    duplicate_policy: str
    size_policy: SizePolicy


def _table(values: Mapping[str, Any], name: str, accepted_keys: tuple[str, ...]) -> Mapping[str, Any]:
    value = values.get(name)
    if value is None:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration is missing required table [{name}]"
        )
    if not isinstance(value, Mapping):
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{name}] must be a table, got {type(value).__name__}"
        )
    unknown = [key for key in value if key not in accepted_keys]
    if unknown:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration table [{name}] contains unknown producer keys: {unknown}"
        )
    return value


def _require_str(table: Mapping[str, Any], table_name: str, field: str, *, path: str) -> str:
    value = table.get(field)
    if value is None:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration is missing required field [{path}]"
        )
    if not isinstance(value, str) or not value:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{path}] must be a non-empty string"
        )
    return value


def _require_bool(table: Mapping[str, Any], table_name: str, field: str, *, path: str) -> bool:
    value = table.get(field)
    if value is None:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration is missing required field [{path}]"
        )
    if not isinstance(value, bool):
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{path}] must be a boolean, got {type(value).__name__}"
        )
    return value


def _require_int(
    table: Mapping[str, Any], table_name: str, field: str, *, path: str, minimum: int
) -> int:
    value = table.get(field)
    if value is None:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration is missing required field [{path}]"
        )
    if not isinstance(value, int) or isinstance(value, bool):
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{path}] must be an integer, got {type(value).__name__}"
        )
    if value < minimum:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{path}] must be >= {minimum}, got {value}"
        )
    return value


def _require_float_between(
    table: Mapping[str, Any], field: str, *, path: str, low: float, high: float
) -> float:
    value = table.get(field)
    if value is None:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration is missing required field [{path}]"
        )
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{path}] must be a real number, got {value!r}"
        )
    as_float = float(value)
    if not (low <= as_float <= high):
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{path}] must be in [{low}, {high}], got {as_float}"
        )
    return as_float


def _enum_choice(table: Mapping[str, Any], field: str, *, path: str, valid: tuple[str, ...]) -> str:
    value = _require_str(table, "generator", field, path=path).lower()
    if value not in valid:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{path}] must be one of {sorted(valid)}, got {value!r}"
        )
    return value


def _require_size_tuple(table: Mapping[str, Any], key: str, *, path: str) -> tuple[int, int]:
    """Validate and return an explicit ``room_count`` tuple ``(min, max)``."""
    value = table.get(key)
    if value is None:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration is missing required field [{path}]"
        )
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{path}] must be a [min, max] pair, got {value!r}"
        )
    low, high = value
    if (
        isinstance(low, bool)
        or isinstance(high, bool)
        or not isinstance(low, int)
        or not isinstance(high, int)
    ):
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{path}] must contain two integers, got {value!r}"
        )
    if low < 1 or high < low:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration field [{path}] must satisfy 1 <= min <= max, got {value!r}"
        )
    return (low, high)


def _resolve_profile(params: Mapping[str, Any]) -> GeneratorProfile:
    """Resolve the complete effective generator parameter declaration.

    The supported scientific surface is validated key-by-key;
    any omitted field resolves through the EHP-owned defaults, so
    the resulting :class:`GeneratorProfile` is always complete and explicit and
    nothing is silently inherited from a mutable upstream default.

    Mutual-exclusion: ``size`` and ``room_count`` may not both be set
    in the same config. ``room_count`` is an optional explicit override; when
    absent, ``size`` alone determines room count (upstream-owned, Correction 3).
    """
    unknown = [key for key in params if key not in SUPPORTED_PARAM_FIELDS]
    if unknown:
        raise DungeonGenConfigurationError(
            f"DungeonGen [generator.params] contains unknown producer keys: {unknown}"
        )

    if "size" in params and "room_count" in params:
        raise DungeonGenConfigurationError(
            "DungeonGen [generator.params] may set only one of size / room_count: "
            "room_count is an explicit override that is mutually exclusive with size."
        )

    # Effective values: user-supplied over the EHP-owned defaults.
    effective = {**_EHP_PARAM_DEFAULTS, **params}

    return GeneratorProfile(
        archetype=_enum_choice(
            effective, "archetype", path="generator.params.archetype", valid=VALID_ARCHETYPES
        ),
        size=_enum_choice(effective, "size", path="generator.params.size", valid=VALID_SIZES),
        room_count=(
            _require_size_tuple(params, "room_count", path="generator.params.room_count")
            if "room_count" in params
            else None
        ),
        room_size_bias=_require_float_between(
            effective, "room_size_bias", path="generator.params.room_size_bias", low=-1.0, high=1.0
        ),
        round_room_chance=_require_float_between(
            effective,
            "round_room_chance",
            path="generator.params.round_room_chance",
            low=0.0,
            high=1.0,
        ),
        hall_chance=_require_float_between(
            effective, "hall_chance", path="generator.params.hall_chance", low=0.0, high=1.0
        ),
        density=_require_float_between(
            effective, "density", path="generator.params.density", low=0.0, high=1.0
        ),
        symmetry=_enum_choice(
            effective, "symmetry", path="generator.params.symmetry", valid=VALID_SYMMETRIES
        ),
        symmetry_break=_require_float_between(
            effective, "symmetry_break", path="generator.params.symmetry_break", low=0.0, high=1.0
        ),
        linearity=_require_float_between(
            effective, "linearity", path="generator.params.linearity", low=0.0, high=1.0
        ),
        loop_factor=_require_float_between(
            effective, "loop_factor", path="generator.params.loop_factor", low=0.0, high=1.0
        ),
        passage_width=_require_int(
            effective, "generator", "passage_width", path="generator.params.passage_width", minimum=1
        ),
        winding=_require_float_between(
            effective, "winding", path="generator.params.winding", low=0.0, high=1.0
        ),
        extra_room_connections=_require_float_between(
            effective,
            "extra_room_connections",
            path="generator.params.extra_room_connections",
            low=0.0,
            high=1.0,
        ),
        extra_passage_junctions=_require_float_between(
            effective,
            "extra_passage_junctions",
            path="generator.params.extra_passage_junctions",
            low=0.0,
            high=1.0,
        ),
        levels=_require_int(effective, "generator", "levels", path="generator.params.levels", minimum=1),
        stair_frequency=_require_float_between(
            effective, "stair_frequency", path="generator.params.stair_frequency", low=0.0, high=1.0
        ),
        water_enabled=_require_bool(
            effective, "generator", "water_enabled", path="generator.params.water_enabled"
        ),
        water_threshold=_require_float_between(
            effective, "water_threshold", path="generator.params.water_threshold", low=-1.0, high=1.0
        ),
    )


def _resolve_size_policy(table: Mapping[str, Any]) -> SizePolicy:
    size = table.get("size_policy")
    if size is None:
        raise DungeonGenConfigurationError(
            "DungeonGen configuration is missing required table [topology.size_policy]"
        )
    if not isinstance(size, Mapping):
        raise DungeonGenConfigurationError(
            "DungeonGen configuration field [topology.size_policy] must be a table, "
            f"got {type(size).__name__}"
        )
    unknown = [key for key in size if key not in _ACCEPTED_SIZE_POLICY_KEYS]
    if unknown:
        raise DungeonGenConfigurationError(
            f"DungeonGen [topology.size_policy] contains unknown producer keys: {unknown}"
        )
    missing = [f for f in _ACCEPTED_SIZE_POLICY_KEYS if f not in size]
    if missing:
        raise DungeonGenConfigurationError(
            f"DungeonGen [topology.size_policy] is missing required fields: {missing}"
        )
    return SizePolicy(
        minimum_height=_require_int(
            size, "topology", "minimum_height", path="topology.size_policy.minimum_height", minimum=1
        ),
        maximum_height=_require_int(
            size, "topology", "maximum_height", path="topology.size_policy.maximum_height", minimum=1
        ),
        minimum_width=_require_int(
            size, "topology", "minimum_width", path="topology.size_policy.minimum_width", minimum=1
        ),
        maximum_width=_require_int(
            size, "topology", "maximum_width", path="topology.size_policy.maximum_width", minimum=1
        ),
        minimum_states=_require_int(
            size, "topology", "minimum_states", path="topology.size_policy.minimum_states", minimum=1
        ),
        maximum_states=_require_int(
            size, "topology", "maximum_states", path="topology.size_policy.maximum_states", minimum=1
        ),
    )


def resolve_configuration(document: LoadedConfiguration) -> DungeonGenConfiguration:
    """Resolve a generic loaded configuration document into a DungeonGen configuration.

    Interprets the parsed values of ``document`` as a DungeonGen v1
    configuration, validates every DungeonGen scientific invariant, and returns
    an immutable, fully effective :class:`DungeonGenConfiguration`.

    It performs **no** file loading, generator access, identity calculation,
    planning, conversion, or CLI translation.
    """
    values = document.values

    missing_tables = [t for t in _REQUIRED_TOP_LEVEL_TABLES if t not in values]
    if missing_tables:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration is missing required tables: {missing_tables}"
        )

    substrate = _table(values, "substrate", _ACCEPTED_SUBSTRATE_KEYS)
    generator = _table(values, "generator", _ACCEPTED_GENERATOR_KEYS)
    conversion = _table(values, "conversion", _ACCEPTED_CONVERSION_KEYS)
    acceptance = _table(values, "acceptance", _ACCEPTED_ACCEPTANCE_KEYS)
    generation = _table(values, "generation", _ACCEPTED_GENERATION_KEYS)
    topology = _table(values, "topology", _ACCEPTED_TOPOLOGY_KEYS)

    variant = _require_str(substrate, "substrate", "variant", path="substrate.variant")
    if variant != VALID_VARIANT:
        raise DungeonGenConfigurationError(
            f"DungeonGen configuration variant must be {VALID_VARIANT!r}, got {variant!r}"
        )

    dependency = _require_str(generator, "generator", "dependency", path="generator.dependency")
    if dependency != DEPENDENCY_REFERENCE:
        raise DungeonGenConfigurationError(
            "DungeonGen generator dependency must be the frozen reference "
            f"{DEPENDENCY_REFERENCE!r}, got {dependency!r}"
        )
    protocol = _require_str(generator, "generator", "protocol", path="generator.protocol")
    if protocol != PROTOCOL_REFERENCE:
        raise DungeonGenConfigurationError(
            "DungeonGen generator protocol must be the frozen reference "
            f"{PROTOCOL_REFERENCE!r}, got {protocol!r}"
        )
    profile_ref = _require_str(generator, "generator", "profile", path="generator.profile")
    if profile_ref != PROFILE_REFERENCE:
        raise DungeonGenConfigurationError(
            "DungeonGen generator profile must be the frozen reference "
            f"{PROFILE_REFERENCE!r}, got {profile_ref!r}"
        )
    profile = _resolve_profile(generator.get("params", {}))

    conversion_policy = _require_str(conversion, "conversion", "policy", path="conversion.policy")
    if conversion_policy != CONVERSION_POLICY:
        raise DungeonGenConfigurationError(
            "DungeonGen conversion policy must be the frozen reference "
            f"{CONVERSION_POLICY!r}, got {conversion_policy!r}"
        )

    acceptance_policy = _require_str(acceptance, "acceptance", "policy", path="acceptance.policy")
    if acceptance_policy != ACCEPTANCE_POLICY:
        raise DungeonGenConfigurationError(
            "DungeonGen acceptance policy must be the frozen reference "
            f"{ACCEPTANCE_POLICY!r}, got {acceptance_policy!r}"
        )
    require_connected = _require_bool(
        acceptance, "acceptance", "require_connected", path="acceptance.require_connected"
    )

    attempt_budget = _require_int(
        generation, "generation", "attempt_budget", path="generation.attempt_budget", minimum=1
    )
    seed = _require_int(generation, "generation", "seed", path="generation.seed", minimum=0)
    record_count = _require_int(
        generation, "generation", "record_count", path="generation.record_count", minimum=1
    )
    randomness_role = _require_str(generation, "generation", "role", path="generation.role")
    if randomness_role != RANDOMNESS_ROLE:
        raise DungeonGenConfigurationError(
            "DungeonGen generation randomness role must be the frozen label "
            f"{RANDOMNESS_ROLE!r}, got {randomness_role!r}"
        )

    duplicate_policy = _require_str(
        topology, "topology", "duplicate_policy", path="topology.duplicate_policy"
    )
    if duplicate_policy not in VALID_DUPLICATE_POLICIES:
        raise DungeonGenConfigurationError(
            "DungeonGen duplicate policy must be one of "
            f"{sorted(VALID_DUPLICATE_POLICIES)}, got {duplicate_policy!r}"
        )
    if duplicate_policy not in SUPPORTED_DUPLICATE_POLICIES:
        raise DungeonGenConfigurationError(
            "DungeonGen duplicate policy "
            f"{duplicate_policy!r} is valid but not yet implemented for the "
            "first release; the first executable profile supports only "
            f"{sorted(SUPPORTED_DUPLICATE_POLICIES)}. It is rejected cleanly "
            "rather than silently downgraded."
        )
    size_policy = _resolve_size_policy(topology)

    return DungeonGenConfiguration(
        variant=variant,
        generator_dependency=dependency,
        generator_protocol=protocol,
        generator_profile=profile_ref,
        profile=profile,
        conversion_policy=conversion_policy,
        component_selection_policy=COMPONENT_SELECTION_POLICY,
        acceptance_policy=acceptance_policy,
        require_connected=require_connected,
        randomness_role=randomness_role,
        seed=seed,
        record_count=record_count,
        attempt_budget=attempt_budget,
        duplicate_policy=duplicate_policy,
        size_policy=size_policy,
    )


__all__ = [
    "DungeonGenConfiguration",
    "DungeonGenConfigurationError",
    "GeneratorProfile",
    "SizePolicy",
    "acceptance_policy_value",
    "profile_identity_values",
    "resolve_configuration",
]


def acceptance_policy_value(configuration: DungeonGenConfiguration) -> str:
    """The canonical acceptance-policy identity value.

    Combines the policy reference and the resolved acceptance conditions into
    one stable identity-bearing value. Conditions are enumerated in a fixed
    order so an equal policy always yields an equal identity value.
    """
    sp = configuration.size_policy
    conditions = (
        f"require_connected={str(configuration.require_connected).lower()}",
        f"min_h={sp.minimum_height}",
        f"max_h={sp.maximum_height}",
        f"min_w={sp.minimum_width}",
        f"max_w={sp.maximum_width}",
        f"min_s={sp.minimum_states}",
        f"max_s={sp.maximum_states}",
    )
    return f"{configuration.acceptance_policy}(" + ";".join(conditions) + ")"


def profile_identity_values(profile: GeneratorProfile) -> dict[str, object]:
    """The generator parameter declaration as one canonical identity value.

    Encodes every resolved effective profile field so the declaration
    participates in build-input identity. ``room_count`` is included
    only when set: a ``None`` room count is exactly the "derive from size" state
    already captured by ``size`` and is therefore not identity-bearing, while an
    explicit ``room_count`` overrides the size-derived count and must alter
    identity.
    """
    values: dict[str, object] = {
        "archetype": profile.archetype,
        "size": profile.size,
        "room_size_bias": profile.room_size_bias,
        "round_room_chance": profile.round_room_chance,
        "hall_chance": profile.hall_chance,
        "density": profile.density,
        "symmetry": profile.symmetry,
        "symmetry_break": profile.symmetry_break,
        "linearity": profile.linearity,
        "loop_factor": profile.loop_factor,
        "passage_width": profile.passage_width,
        "winding": profile.winding,
        "extra_room_connections": profile.extra_room_connections,
        "extra_passage_junctions": profile.extra_passage_junctions,
        "levels": profile.levels,
        "stair_frequency": profile.stair_frequency,
        "water_enabled": profile.water_enabled,
        "water_threshold": profile.water_threshold,
    }
    if profile.room_count is not None:
        values["room_count"] = list(profile.room_count)
    return values
