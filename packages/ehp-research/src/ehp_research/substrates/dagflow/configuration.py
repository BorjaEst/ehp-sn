"""Authoritative Dagflow v1 producer-owned configuration resolution.

This module is the single authoritative home for turning the generic
configuration document produced by the framework configuration loader
(Capability 4, ``ehp_sn.configuration.load_configuration``) into the
immutable, fully effective Dagflow scientific configuration.

It owns only Dagflow semantics. It interprets a generic parsed document
(:class:`~ehp_sn.configuration.LoadedConfiguration`) as a valid Dagflow
configuration — nothing more. The concrete pipeline it implements is::

    generic parsed configuration
            ↓
    dagflow.resolve_configuration(document)
            ↓
    DagflowConfiguration (immutable, fully effective)

It deliberately does **not**:

* load files, open sources, or perform any I/O;
* bind resources, resolve physical locations, or select artifacts;
* compute build-input identities, fingerprints, or digests;
* plan, generate graphs, or execute the producer;
* translate to a CLI-facing error (no exit-code semantics).

Scientific validation and normative/default handling happen here; generic
*loading* mechanics stay in ``ehp_sn.configuration``. Gate-keeping is
deliberate: the framework knows that TOML is readable; this module knows what
a *valid Dagflow configuration* is.

Fields are derived strictly from the authoritative specification
``docs/docs/research/substrates/dagflow-v1.md`` § "Configuration and
family-specific identity inputs" and from the actual reusable repository
profiles under ``config/data/dagflow/``. No field is invented.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

from ehp_sn.configuration import LoadedConfiguration

#: The only valid ``single-terminal`` variant for dagflow/v1. The specification
#: defines exactly one consumer-visible structural variant; any other value is
#: not a valid Dagflow v1 configuration.
VALID_VARIANT: Final = "single-terminal"

#: Field names of the bounded-distribution node-count policy, declared
#: together inside the ``graph.node_count`` table.
_BOUNDED_POLICY_FIELDS: Final = ("minimum", "maximum", "distribution")

_REQUIRED_TOP_LEVEL_TABLES: Final = ("substrate", "generation", "graph", "splits")
_REQUIRED_SPLIT_FIELDS: Final = ("train", "validation", "test")


class DagflowConfigurationError(ValueError):
    """A loaded configuration is not a valid Dagflow v1 configuration.

    Raised by :func:`resolve_configuration` when the generic configuration
    document violates a Dagflow scientific invariant: a required field is
    missing, a value is out of range, or a protocol/value combination is
    invalid. It is a Dagflow-owned semantic error, not a framework loading or
    CLI error; the orchestration/CLI boundary translates it at its own layer.
    """


@dataclass(frozen=True)
class DagflowConfiguration:
    """Immutable, fully effective Dagflow v1 scientific configuration.

    This object means *validated Dagflow configuration*: every scientific
    choice has been checked and, where the specification defines a normative
    default, applied. It is a resolved, effective Dagflow configuration — not a
    generic parsed TOML document.

    ``variant`` is always the validated ``single-terminal`` value. Exactly one
    node-count policy is present: either ``node_count`` (fixed policy) or the
    full bounded triple (``node_count_minimum`` / ``node_count_maximum`` /
    ``node_count_distribution``). The inactive policy fields are ``None``.

    The object carries no resource binding, identity, plan, or execution
    state. The  ``generation_protocol`` and ``seed`` are scientific inputs used
    by later planning (Capability 6), not resolved physical resources.
    """

    variant: str
    generation_protocol: str
    seed: int
    node_count: int | None
    node_count_minimum: int | None
    node_count_maximum: int | None
    node_count_distribution: str | None
    additional_edge_probability: float
    splits_train_count: int
    splits_validation_count: int
    splits_test_count: int


def _table(values: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    """Return the named sub-table or raise a producer configuration error."""
    value = values.get(name)
    if value is None:
        raise DagflowConfigurationError(f"Dagflow configuration is missing required table [{name}]")
    if not isinstance(value, Mapping):
        raise DagflowConfigurationError(
            f"Dagflow configuration field [{name}] must be a table, got {type(value).__name__}"
        )
    return value


def _require_mapping_table(values: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    """Return a present sub-table as a mapping, or raise if it is not a table.

    Unlike :func:`_table`, presence is assumed to have been checked by the
    caller; this only verifies the value has table shape.
    """
    value = values[name]
    if not isinstance(value, Mapping):
        raise DagflowConfigurationError(
            f"Dagflow configuration field [{name}] must be a table, got {type(value).__name__}"
        )
    return value


def _require_int_table_field(
    table: Mapping[str, Any], table_name: str, field: str, *, minimum: int
) -> int:
    value = table.get(field)
    if value is None:
        raise DagflowConfigurationError(
            f"Dagflow configuration is missing required field [{table_name}.{field}]"
        )
    if not isinstance(value, int) or isinstance(value, bool):
        raise DagflowConfigurationError(
            f"Dagflow configuration field [{table_name}.{field}] must be an integer, "
            f"got {type(value).__name__}"
        )
    if value < minimum:
        raise DagflowConfigurationError(
            f"Dagflow configuration field [{table_name}.{field}] must be >= {minimum}, got {value}"
        )
    return value


def _require_str_table_field(table: Mapping[str, Any], table_name: str, field: str) -> str:
    value = table.get(field)
    if value is None:
        raise DagflowConfigurationError(
            f"Dagflow configuration is missing required field [{table_name}.{field}]"
        )
    if not isinstance(value, str):
        raise DagflowConfigurationError(
            f"Dagflow configuration field [{table_name}.{field}] must be a string, "
            f"got {type(value).__name__}"
        )
    if not value:
        raise DagflowConfigurationError(
            f"Dagflow configuration field [{table_name}.{field}] must not be empty"
        )
    return value


def _resolve_node_count_policy(
    graph: Mapping[str, Any],
) -> tuple[int | None, int | None, int | None, str | None]:
    """Validate and resolve exactly one node-count policy.

    The specification permits exactly one policy. ``graph.node_count`` is the
    single node-count policy key: either a fixed integer (fixed policy) or the
    complete bounded-distribution table ``{minimum, maximum, distribution}``
    (bounded policy). A fixed integer and the bounded triple are mutually
    exclusive by construction (the same key cannot be both an integer and a
    table).

    Returns ``(node_count, minimum, maximum, distribution)`` where the inactive
    policy is ``None``. Raises :class:`DagflowConfigurationError` for a missing
    policy, a partial bounded triple, a malformed value, or an out-of-range
    bound.
    """
    policy = graph.get("node_count")
    if policy is None:
        raise DagflowConfigurationError(
            "Dagflow configuration requires a node-count policy: either fixed "
            "graph.node_count (integer) or the complete bounded "
            "graph.node_count.{minimum,maximum,distribution} table"
        )

    # ``bool`` is a subclass of ``int`` but is not a valid node count; reject it
    # before accepting the fixed-integer policy.
    if isinstance(policy, bool):
        raise DagflowConfigurationError(
            "Dagflow configuration field [graph.node_count] must be an integer, "
            "not a boolean, for the fixed policy"
        )
    if isinstance(policy, int):
        if policy < 1:
            raise DagflowConfigurationError(
                "Dagflow configuration field [graph.node_count] must be >= 1 "
                f"for the fixed policy, got {policy}"
            )
        return policy, None, None, None

    if not isinstance(policy, Mapping):
        raise DagflowConfigurationError(
            "Dagflow configuration field [graph.node_count] must be an integer "
            "(fixed policy) or a table (bounded policy), "
            f"got {type(policy).__name__}"
        )

    missing = [field for field in _BOUNDED_POLICY_FIELDS if field not in policy]
    if missing:
        raise DagflowConfigurationError(
            "Dagflow bounded node-count policy must declare the complete "
            f"graph.node_count.{{minimum,maximum,distribution}} table; missing: "
            f"{['node_count.' + f for f in missing]}"
        )

    minimum = policy["minimum"]
    maximum = policy["maximum"]
    distribution = policy["distribution"]
    if isinstance(minimum, bool) or not isinstance(minimum, int):
        raise DagflowConfigurationError(
            "Dagflow configuration field [graph.node_count.minimum] must be an "
            f"integer, got {type(minimum).__name__}"
        )
    if isinstance(maximum, bool) or not isinstance(maximum, int):
        raise DagflowConfigurationError(
            "Dagflow configuration field [graph.node_count.maximum] must be an "
            f"integer, got {type(maximum).__name__}"
        )
    if not isinstance(distribution, str) or not distribution:
        raise DagflowConfigurationError(
            "Dagflow configuration field [graph.node_count.distribution] must be a non-empty string"
        )
    if minimum < 1:
        raise DagflowConfigurationError(
            f"Dagflow configuration field [graph.node_count.minimum] must be >= 1, got {minimum}"
        )
    if maximum < minimum:
        raise DagflowConfigurationError(
            "Dagflow bounded node-count policy requires graph.node_count.maximum >= "
            f"graph.node_count.minimum (got maximum={maximum} < minimum={minimum})"
        )

    return None, minimum, maximum, distribution


def resolve_configuration(document: LoadedConfiguration) -> DagflowConfiguration:
    """Resolve a generic loaded configuration document into a Dagflow configuration.

    Interprets the parsed values of ``document`` (Capability 4's generic
    representation — not a raw TOML path) as a Dagflow v1 configuration. It
    validates every Dagflow scientific invariant, applies only documented
    Dagflow defaults, and returns an immutable, fully effective
    :class:`DagflowConfiguration`.

    It performs **no** file loading (the loader already did that), resource
    binding, identity calculation, planning, graph generation, or CLI
    translation.

    Raises:

    * :class:`DagflowConfigurationError` if the document is not a valid Dagflow
      v1 configuration.
    """
    values = document.values

    missing_tables = [t for t in _REQUIRED_TOP_LEVEL_TABLES if t not in values]
    if missing_tables:
        raise DagflowConfigurationError(
            f"Dagflow configuration is missing required tables: {missing_tables}"
        )

    substrate = _table(values, "substrate")
    generation = _table(values, "generation")
    graph = _table(values, "graph")
    splits = _table(values, "splits")

    variant = _require_str_table_field(substrate, "substrate", "variant")
    if variant != VALID_VARIANT:
        raise DagflowConfigurationError(
            f"Dagflow configuration variant must be {VALID_VARIANT!r}, got {variant!r}"
        )

    generation_protocol = _require_str_table_field(generation, "generation", "protocol")
    seed = _require_int_table_field(generation, "generation", "seed", minimum=0)

    node_count, minimum, maximum, distribution = _resolve_node_count_policy(graph)

    probability = graph.get("additional_edge_probability")
    if probability is None:
        raise DagflowConfigurationError(
            "Dagflow configuration is missing required field [graph.additional_edge_probability]"
        )
    if not isinstance(probability, (int, float)) or isinstance(probability, bool):
        raise DagflowConfigurationError(
            "Dagflow configuration field [graph.additional_edge_probability] must be a real "
            f"number, got {type(probability).__name__}"
        )
    probability_value = float(probability)
    if not 0.0 <= probability_value <= 1.0:
        raise DagflowConfigurationError(
            "Dagflow configuration field [graph.additional_edge_probability] must be in [0, 1], "
            f"got {probability_value}"
        )

    missing_splits = [s for s in _REQUIRED_SPLIT_FIELDS if s not in splits]
    if missing_splits:
        raise DagflowConfigurationError(
            f"Dagflow configuration is missing required split tables: {missing_splits}"
        )

    train_split = _require_mapping_table(splits, "train")
    validation_split = _require_mapping_table(splits, "validation")
    test_split = _require_mapping_table(splits, "test")
    splits_train = _require_int_table_field(train_split, "splits.train", "count", minimum=0)
    splits_validation = _require_int_table_field(
        validation_split, "splits.validation", "count", minimum=0
    )
    splits_test = _require_int_table_field(test_split, "splits.test", "count", minimum=0)

    return DagflowConfiguration(
        variant=variant,
        generation_protocol=generation_protocol,
        seed=seed,
        node_count=node_count,
        node_count_minimum=minimum,
        node_count_maximum=maximum,
        node_count_distribution=distribution,
        additional_edge_probability=probability_value,
        splits_train_count=splits_train,
        splits_validation_count=splits_validation,
        splits_test_count=splits_test,
    )


__all__ = [
    "DagflowConfiguration",
    "DagflowConfigurationError",
    "resolve_configuration",
]
