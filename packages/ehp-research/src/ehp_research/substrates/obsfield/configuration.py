"""Authoritative ObsField v1 producer-owned configuration resolution.

This module is the single authoritative home for turning the generic
configuration document produced by the framework configuration loader
(``ehp_sn.configuration.load_configuration``) into the immutable, fully
effective ObsField scientific configuration.

It owns only ObsField semantics. It interprets a generic parsed document
(:class:`~ehp_sn.configuration.LoadedConfiguration`) as a valid ObsField
configuration — nothing more.

The configuration mirrors the reusable profiles under ``config/data/obsfield/``
(``uniform-random.toml``, ``weighted-random.toml``) and the authoritative
specification ``docs/docs/research/substrates/obsfield-v1.md``.

It deliberately does **not** load files, bind resources, generate fields, plan,
or translate to a CLI-facing error.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from ehp_sn.configuration import LoadedConfiguration

#: The only valid ``categorical-complete`` variant for obsfield/v1.
VALID_VARIANT: Final = "categorical-complete"
#: The only registered domain schema for the first executable profile.
VALID_DOMAIN_SCHEMA: Final = "rectangular-row-column/v1"
#: The only registered assignment protocol for the first executable profile.
REQUIRED_PROTOCOL: Final = "categorical-random/v1"

_REQUIRED_TOP_LEVEL_TABLES: Final = ("substrate", "domain", "vocabulary", "assignment", "generation")

#: Categorical distribution declaration for ``categorical-random/v1``.
#: Either the string ``"uniform"`` (every entry probability ``1/K``) or an
#: explicit probability vector of length ``K``.
Distribution = str | tuple[float, ...]


class ObsFieldConfigurationError(ValueError):
    """A loaded configuration is not a valid ObsField v1 configuration.

    Raised by :func:`resolve_configuration` when the document violates an
    ObsField scientific invariant. It is an ObsField-owned semantic error, not a
    framework loading or CLI error.
    """


@dataclass(frozen=True)
class ObsFieldConfiguration:
    """Immutable, fully effective ObsField v1 scientific configuration.

    ``variant`` is always the validated ``categorical-complete`` value.
    ``distribution`` is either ``"uniform"`` or an explicit categorical
    probability vector over the vocabulary. ``realization_count`` is the number
    of observation realizations requested per declared domain/configuration.
    """

    variant: str
    domain_schema: str
    height: int
    width: int
    vocabulary_identity: str
    vocabulary_cardinality: int
    assignment_protocol: str
    distribution: Distribution
    seed: int
    realization_count: int


def _table(values: Mapping[str, object], name: str) -> Mapping[str, object]:
    """Return the named sub-table or raise a producer configuration error."""
    value = values.get(name)
    if value is None:
        raise ObsFieldConfigurationError(f"ObsField configuration is missing required table [{name}]")
    if not isinstance(value, Mapping):
        raise ObsFieldConfigurationError(
            f"ObsField configuration field [{name}] must be a table, got {type(value).__name__}"
        )
    return value


def _require_str(table: Mapping[str, object], table_name: str, field: str) -> str:
    value = table.get(field)
    if value is None:
        raise ObsFieldConfigurationError(
            f"ObsField configuration is missing required field [{table_name}.{field}]"
        )
    if not isinstance(value, str) or not value:
        raise ObsFieldConfigurationError(
            f"ObsField configuration field [{table_name}.{field}] must be a non-empty string"
        )
    return value


def _require_int(table: Mapping[str, object], table_name: str, field: str, *, minimum: int) -> int:
    value = table.get(field)
    if value is None:
        raise ObsFieldConfigurationError(
            f"ObsField configuration is missing required field [{table_name}.{field}]"
        )
    if not isinstance(value, int) or isinstance(value, bool):
        raise ObsFieldConfigurationError(
            f"ObsField configuration field [{table_name}.{field}] must be an integer, "
            f"got {type(value).__name__}"
        )
    if value < minimum:
        raise ObsFieldConfigurationError(
            f"ObsField configuration field [{table_name}.{field}] must be >= {minimum}, got {value}"
        )
    return value


def _resolve_distribution(
    parameters: Mapping[str, object],
    cardinality: int,
) -> Distribution:
    """Resolve and validate the ``categorical-random/v1`` distribution.

    Returns ``"uniform"`` for the canonical uniform declaration, or an explicit
    probability vector of length ``K`` that sums to ``1`` (within a tolerance).
    """
    value = parameters.get("distribution")
    if value is None:
        raise ObsFieldConfigurationError(
            "ObsField configuration is missing required field [assignment.parameters.distribution]"
        )
    if value == "uniform":
        return "uniform"

    # An explicit categorical probability vector.
    if isinstance(value, Mapping):
        raise ObsFieldConfigurationError(
            "ObsField distribution must be 'uniform' or a probability vector, not a table"
        )
    if isinstance(value, (str, bytes)):
        raise ObsFieldConfigurationError(
            f"ObsField distribution must be 'uniform' or a probability vector, got {value!r}"
        )
    if not isinstance(value, Sequence):
        raise ObsFieldConfigurationError(
            "ObsField distribution must be 'uniform' or a probability vector, "
            f"got {type(value).__name__}"
        )

    vector = list(value)
    if len(vector) != cardinality:
        raise ObsFieldConfigurationError(
            f"ObsField probability vector length {len(vector)} != vocabulary cardinality {cardinality}"
        )
    floats: list[float] = []
    for item in vector:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ObsFieldConfigurationError(
                f"ObsField probability vector entries must be reals, got {item!r}"
            )
        floats.append(float(item))
    if any(p < 0.0 for p in floats):
        raise ObsFieldConfigurationError("ObsField probability vector entries must be >= 0")
    total = sum(floats)
    if abs(total - 1.0) > 1e-9:
        raise ObsFieldConfigurationError(f"ObsField probability vector must sum to 1, got {total}")
    return tuple(floats)


def resolve_configuration(document: LoadedConfiguration) -> ObsFieldConfiguration:
    """Resolve a generic loaded configuration document into an ObsField configuration.

    Interprets the parsed values of ``document`` as an ObsField v1 configuration,
    validates every ObsField scientific invariant, and returns an immutable,
    fully effective :class:`ObsFieldConfiguration`.
    """
    values = document.values
    missing = [t for t in _REQUIRED_TOP_LEVEL_TABLES if t not in values]
    if missing:
        raise ObsFieldConfigurationError(f"ObsField configuration is missing required tables: {missing}")

    substrate = _table(values, "substrate")
    domain = _table(values, "domain")
    vocabulary = _table(values, "vocabulary")
    assignment = _table(values, "assignment")
    generation = _table(values, "generation")

    variant = _require_str(substrate, "substrate", "variant")
    if variant != VALID_VARIANT:
        raise ObsFieldConfigurationError(
            f"ObsField configuration variant must be {VALID_VARIANT!r}, got {variant!r}"
        )

    domain_schema = _require_str(domain, "domain", "schema")
    if domain_schema != VALID_DOMAIN_SCHEMA:
        raise ObsFieldConfigurationError(
            f"ObsField domain schema must be {VALID_DOMAIN_SCHEMA!r}, got {domain_schema!r}"
        )
    height = _require_int(domain, "domain", "height", minimum=1)
    width = _require_int(domain, "domain", "width", minimum=1)

    vocabulary_identity = _require_str(vocabulary, "vocabulary", "identity")
    cardinality = _require_int(vocabulary, "vocabulary", "cardinality", minimum=1)

    protocol = _require_str(assignment, "assignment", "protocol")
    if protocol != REQUIRED_PROTOCOL:
        raise ObsFieldConfigurationError(
            f"ObsField assignment protocol must be {REQUIRED_PROTOCOL!r}, got {protocol!r}"
        )

    parameters = _table(assignment, "parameters")
    distribution = _resolve_distribution(parameters, cardinality)

    seed = _require_int(generation, "generation", "seed", minimum=0)
    realization_count = _require_int(generation, "generation", "realization_count", minimum=1)

    return ObsFieldConfiguration(
        variant=variant,
        domain_schema=domain_schema,
        height=height,
        width=width,
        vocabulary_identity=vocabulary_identity,
        vocabulary_cardinality=cardinality,
        assignment_protocol=protocol,
        distribution=distribution,
        seed=seed,
        realization_count=realization_count,
    )


__all__ = [
    "Distribution",
    "ObsFieldConfiguration",
    "ObsFieldConfigurationError",
    "REQUIRED_PROTOCOL",
    "VALID_DOMAIN_SCHEMA",
    "VALID_VARIANT",
    "resolve_configuration",
]
