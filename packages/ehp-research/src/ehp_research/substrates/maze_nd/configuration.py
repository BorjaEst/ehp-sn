"""Authoritative Maze-ND v1 producer-owned configuration resolution.

This module is the single authoritative home for turning the generic
configuration document produced by the framework configuration loader
(Capability 4, ``ehp_sn.configuration.load_configuration``) into the
immutable, fully effective Maze-ND scientific configuration.

It owns only Maze-ND semantics. It interprets a generic parsed document
(:class:`~ehp_sn.configuration.LoadedConfiguration`) as a valid Maze-ND
configuration — nothing more. The concrete pipeline it implements is::

    generic parsed configuration
            ↓
    maze_nd.resolve_configuration(document)
            ↓
    MazeNDConfiguration (immutable, fully effective)

It deliberately does **not**:

* load files, open sources, download, or inspect ``data/raw``;
* bind resources or resolve where a source lives;
* compute build-input identities, fingerprints, or digests;
* plan, extract, normalize, deduplicate, or execute the producer;
* translate to a CLI-facing error (no exit-code semantics).

The Maze-ND resolver declares the upstream *source requirement* — reference,
revision, fingerprint, and schema — as carried scientific state. It does **not**
verify the source exists or bind it to a physical location; that is framework
resource resolution (Capability 6) and is deliberately out of scope here.

Fields are derived strictly from the authoritative specification
``docs/docs/research/substrates/maze-nd-v1.md`` § "Configuration and
family-specific identity inputs" and from the actual reusable repository
profiles under ``config/data/maze-nd/``. No field is invented. Where the
specification leaves a required choice open, the resolver applies **no**
guessed default — a genuinely unresolved required scientific choice remains a
configuration failure unless explicitly declared.

Since the Phase 5.2 source decision, the source revision/fingerprint values
are fixed for the initial release, and the initial connectivity policy is
``reject`` (``connected-source.toml``) with ``preserve`` retained as a reusable
regime (``preserve-disconnected-source.toml``). The resolver carries these as
declared requirement state; it never special-cases a particular value string.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

from ehp_sn.configuration import LoadedConfiguration

#: The only valid ``source-topology`` variant for maze-nd/v1.
VALID_VARIANT: Final = "source-topology"

#: Valid connectivity policies of maze-nd/v1. The source import policy must be
#: one of these. The first release declares ``reject`` (``connected-source.toml``);
#: ``preserve`` (``preserve-disconnected-source.toml``) remains a reusable
#: regime for a future full-population analysis release. No default is applied;
#: a profile must declare one explicitly.
VALID_CONNECTIVITY_POLICIES: Final = ("preserve", "reject")

_REQUIRED_TOP_LEVEL_TABLES: Final = ("substrate", "source", "normalization", "topology")
_REQUIRED_SOURCE_FIELDS: Final = (
    "reference",
    "revision",
    "fingerprint",
    "schema",
    "selection_policy",
    "selection_before_dedup",
)

#: Accepted producer keys per table. Unknown producer keys are rejected so that
#: a typo cannot silently change the meaning of a reproducible scientific
#: profile (reproducibility over permissiveness).
_ACCEPTED_SUBSTRATE_KEYS: Final = ("variant",)
_ACCEPTED_SOURCE_KEYS: Final = _REQUIRED_SOURCE_FIELDS
_ACCEPTED_NORMALIZATION_KEYS: Final = ("policy",)
_ACCEPTED_TOPOLOGY_KEYS: Final = ("connectivity_policy", "deduplication_policy")


class MazeNDConfigurationError(ValueError):
    """A loaded configuration is not a valid Maze-ND v1 configuration.

    Raised by :func:`resolve_configuration` when the generic configuration
    document violates a Maze-ND scientific invariant: a required field is
    missing, an unrecognized producer key is present, an invalid enum value is
    supplied, or a required scientific choice is left genuinely unresolved. It
    is a Maze-ND-owned semantic error, not a framework loading or CLI error;
    the orchestration/CLI boundary translates it at its own layer.
    """


@dataclass(frozen=True)
class MazeNDConfiguration:
    """Immutable, fully effective Maze-ND v1 scientific configuration.

    This object means *validated Maze-ND configuration*: every declared
    scientific choice has been checked and carried into an effective,
    immutable form. It is not a generic parsed TOML document.

    The ``source_*`` fields express the upstream source *requirement* declared
    by the configuration: the authoritative external source reference,
    revision, and content fingerprint, plus the extraction schema. They are
    carried state, not resolved physical locations — resource binding is a
    later framework concern (Capability 6).

    ``connectivity_policy`` is either ``preserve`` or ``reject``; it carries no
    default, and the initial release's choice is fixed per the Phase 5.2 source
    decision in the specification. ``selection_before_dedup`` records the
    mandated selection vs. deduplication ordering.
    """

    variant: str
    source_reference: str
    source_revision: str
    source_fingerprint: str
    source_schema: str
    source_selection_policy: str
    selection_before_dedup: bool
    normalization_policy: str
    connectivity_policy: str
    deduplication_policy: str


def _table(values: Mapping[str, Any], name: str, accepted_keys: tuple[str, ...]) -> Mapping[str, Any]:
    value = values.get(name)
    if value is None:
        raise MazeNDConfigurationError(f"Maze-ND configuration is missing required table [{name}]")
    if not isinstance(value, Mapping):
        raise MazeNDConfigurationError(
            f"Maze-ND configuration field [{name}] must be a table, got {type(value).__name__}"
        )
    unknown = [key for key in value if key not in accepted_keys]
    if unknown:
        raise MazeNDConfigurationError(
            f"Maze-ND configuration table [{name}] contains unknown producer keys: {unknown}"
        )
    return value


def _require_str_choice(table: Mapping[str, Any], table_name: str, field: str, *, path: str) -> str:
    value = table.get(field)
    if value is None:
        raise MazeNDConfigurationError(f"Maze-ND configuration is missing required field [{path}]")
    if not isinstance(value, str):
        raise MazeNDConfigurationError(
            f"Maze-ND configuration field [{path}] must be a string, got {type(value).__name__}"
        )
    if not value:
        raise MazeNDConfigurationError(f"Maze-ND configuration field [{path}] must not be empty")
    return value


def resolve_configuration(document: LoadedConfiguration) -> MazeNDConfiguration:
    """Resolve a generic loaded configuration document into a Maze-ND configuration.

    Interprets the parsed values of ``document`` (Capability 4's generic
    representation — not a raw TOML path) as a Maze-ND v1 configuration. It
    validates every Maze-ND scientific invariant, applies only documented
    Maze-ND defaults (there are none today), and returns an immutable, fully
    effective :class:`MazeNDConfiguration`.

    It performs **no** file loading, source access, resource binding, identity
    calculation, planning, extraction, or CLI translation.

    Raises:

    * :class:`MazeNDConfigurationError` if the document is not a valid Maze-ND
      v1 configuration.
    """
    values = document.values

    missing_tables = [t for t in _REQUIRED_TOP_LEVEL_TABLES if t not in values]
    if missing_tables:
        raise MazeNDConfigurationError(
            f"Maze-ND configuration is missing required tables: {missing_tables}"
        )

    substrate = _table(values, "substrate", _ACCEPTED_SUBSTRATE_KEYS)
    source = _table(values, "source", _ACCEPTED_SOURCE_KEYS)
    normalization = _table(values, "normalization", _ACCEPTED_NORMALIZATION_KEYS)
    topology = _table(values, "topology", _ACCEPTED_TOPOLOGY_KEYS)

    variant = _require_str_choice(substrate, "substrate", "variant", path="substrate.variant")
    if variant != VALID_VARIANT:
        raise MazeNDConfigurationError(
            f"Maze-ND configuration variant must be {VALID_VARIANT!r}, got {variant!r}"
        )

    missing_source_fields = [f for f in _REQUIRED_SOURCE_FIELDS if f not in source]
    if missing_source_fields:
        raise MazeNDConfigurationError(
            f"Maze-ND configuration is missing required source fields: "
            f"{['source.' + f for f in missing_source_fields]}"
        )

    source_reference = _require_str_choice(source, "source", "reference", path="source.reference")
    source_revision = _require_str_choice(source, "source", "revision", path="source.revision")
    source_fingerprint = _require_str_choice(source, "source", "fingerprint", path="source.fingerprint")
    source_schema = _require_str_choice(source, "source", "schema", path="source.schema")
    source_selection_policy = _require_str_choice(
        source, "source", "selection_policy", path="source.selection_policy"
    )

    selection_before_dedup = source.get("selection_before_dedup")
    if not isinstance(selection_before_dedup, bool):
        raise MazeNDConfigurationError(
            "Maze-ND configuration field [source.selection_before_dedup] must be a boolean, "
            f"got {type(selection_before_dedup).__name__}"
        )

    normalization_policy = _require_str_choice(
        normalization, "normalization", "policy", path="normalization.policy"
    )

    connectivity_policy = _require_str_choice(
        topology, "topology", "connectivity_policy", path="topology.connectivity_policy"
    )
    if connectivity_policy not in VALID_CONNECTIVITY_POLICIES:
        raise MazeNDConfigurationError(
            "Maze-ND configuration connectivity policy must be one of "
            f"{sorted(VALID_CONNECTIVITY_POLICIES)}, got {connectivity_policy!r}"
        )

    deduplication_policy = _require_str_choice(
        topology, "topology", "deduplication_policy", path="topology.deduplication_policy"
    )

    return MazeNDConfiguration(
        variant=variant,
        source_reference=source_reference,
        source_revision=source_revision,
        source_fingerprint=source_fingerprint,
        source_schema=source_schema,
        source_selection_policy=source_selection_policy,
        selection_before_dedup=selection_before_dedup,
        normalization_policy=normalization_policy,
        connectivity_policy=connectivity_policy,
        deduplication_policy=deduplication_policy,
    )


__all__ = [
    "MazeNDConfiguration",
    "MazeNDConfigurationError",
    "resolve_configuration",
]
