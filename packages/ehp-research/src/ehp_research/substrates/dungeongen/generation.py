"""DungeonGen candidate generation and deterministic seed derivation.

This module owns the DungeonGen producer steps that turn the resolved
configuration into a *raw native candidate* from the frozen external generator:

* BUILD-readiness verification of the exact installed dependency —
  a wrong or missing ``dungeongen`` yields a controlled readiness failure;
* construction of the complete explicit upstream ``GenerationParams`` from the
  resolved declaration — the declaration is always complete after
  EHP-owned defaults, so nothing is silently inherited from a mutable upstream
  default; ``size`` and ``room_count`` are mutually exclusive;
* record-addressable candidate-seed derivation  — a pure,
  parallel-safe function of ``(base_seed, protocol, profile, i, a, role)``;
* invocation of the exact upstream layout path
  ``DungeonGenerator(params).generate(seed=…)`` and capture of the native
  ``Dungeon`` plus its occupancy raster (source).

The protocol explicitly uses the structured layout subsystem, never the
renderer / webview / drawing / filesystem output.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Final

from ._dependency import (
    PACKAGE_NAME,
    PACKAGE_VERSION,
    UPSTREAM_REVISION,
)
from .configuration import DungeonGenConfiguration, GeneratorProfile

#: The upstream RNG seed space is a non-negative 31-bit integer.
_CANDIDATE_SEED_SPACE_BITS: Final = 31

#: Mirror the upstream 0.1.14 enum value names (lower-cased) to the upstream
#: enum classes, resolved lazily so this module imports without the dependency.
_ARCHETYPE_MAP: Final = {
    "classic": "CLASSIC",
    "warren": "WARREN",
    "temple": "TEMPLE",
    "crypt": "CRYPT",
    "cavern": "CAVERN",
    "fortress": "FORTRESS",
    "lair": "LAIR",
}
_SIZE_MAP: Final = {
    "tiny": "TINY",
    "small": "SMALL",
    "medium": "MEDIUM",
    "large": "LARGE",
    "xlarge": "XLARGE",
}
_SYMMETRY_MAP: Final = {
    "none": "NONE",
    "bilateral": "BILATERAL",
    "radial_2": "RADIAL_2",
    "radial_4": "RADIAL_4",
    "partial": "PARTIAL",
}


class GenerationError(ValueError):
    """A controlled DungeonGen generation or readiness failure.

    Raised for a wrong/missing installed dependency, an unavailable upstream
    layout API, or an unexpected native output. Translated by the executor into
    a controlled candidate rejection or build failure; never a silent
    substitution.
    """


# ---------------------------------------------------------------------------
# BUILD-readiness
# ---------------------------------------------------------------------------


def verify_dependency_build_ready() -> None:
    """Verify the exact installed external generator is present and correct.

    A conforming build must fail controlled (not with an accidental
    ``ImportError``) when the wrong or absent dependency is installed. This
    checks:

    * the ``dungeongen`` package imports;
    * the installed package version equals the frozen ``0.1.14``;
    * the structured layout API surface (``GenerationParams``,
      ``DungeonGenerator``, ``generate``, the occupancy ``CellType``) is present.

    A different installed version than the frozen one is a controlled
    BUILD-readiness failure: it cannot be treated as the frozen dependency.
    """
    try:
        import dungeongen  # noqa: F401
        from dungeongen.layout.generator import DungeonGenerator  # noqa: F401
        from dungeongen.layout.occupancy import CellType  # noqa: F401
        from dungeongen.layout.params import (  # noqa: F401
            GenerationParams,
        )
    except Exception as exc:  # pragma: no cover - defensive
        raise GenerationError(
            f"dungeongen production dependency is not importable; install the "
            f"frozen {PACKAGE_NAME}=={PACKAGE_VERSION} at {UPSTREAM_REVISION} "
            f"({exc.__class__.__name__}: {exc})"
        ) from exc

    installed = getattr(__import__(PACKAGE_NAME), "__version__", None)
    import importlib.metadata as _md

    try:
        installed = _md.version(PACKAGE_NAME)
    except _md.PackageNotFoundError:  # pragma: no cover - defensive
        installed = None
    if installed != PACKAGE_VERSION:
        raise GenerationError(
            f"installed {PACKAGE_NAME} version {installed!r} does not match the "
            f"frozen {PACKAGE_VERSION!r} (upstream revision {UPSTREAM_REVISION}); "
            "the exact dependency identity cannot be reacquired, refusing to run."
        )


# ---------------------------------------------------------------------------
# GenerationParams construction
# ---------------------------------------------------------------------------


def to_upstream_params(profile: GeneratorProfile) -> Any:
    """Build the complete explicit upstream ``GenerationParams`` from the profile.

     Every upstream field is supplied exactly once from the resolved declaration
    ; nothing relies on a mutable upstream default. ``size`` and
     ``room_count`` are mutually exclusive: when a ``room_count`` is
     set it is passed explicitly and wins over ``size`` (which remains EHP-resolved
     at its default and is harmless because the upstream generator overrides the
     auto count when ``room_count`` is set); when absent, ``None`` is passed so
     room count derives from ``size``. Uses the frozen upstream enum names.
    """
    from dungeongen.layout.params import (
        DungeonArchetype,
        DungeonSize,
        GenerationParams,
        SymmetryType,
    )

    return GenerationParams(
        archetype=DungeonArchetype[_ARCHETYPE_MAP[profile.archetype]],
        size=DungeonSize[_SIZE_MAP[profile.size]],
        room_count=profile.room_count,
        room_size_bias=profile.room_size_bias,
        round_room_chance=profile.round_room_chance,
        hall_chance=profile.hall_chance,
        density=profile.density,
        symmetry=SymmetryType[_SYMMETRY_MAP[profile.symmetry]],
        symmetry_break=profile.symmetry_break,
        linearity=profile.linearity,
        loop_factor=profile.loop_factor,
        passage_width=profile.passage_width,
        winding=profile.winding,
        extra_room_connections=profile.extra_room_connections,
        extra_passage_junctions=profile.extra_passage_junctions,
        levels=profile.levels,
        stair_frequency=profile.stair_frequency,
        water_enabled=profile.water_enabled,
        water_threshold=profile.water_threshold,
    )


# ---------------------------------------------------------------------------
# Candidate seed derivation
# ---------------------------------------------------------------------------


def candidate_seed(configuration: DungeonGenConfiguration, index: int, attempt: int) -> int:
    """Return the deterministic candidate seed for logical index ``i`` and attempt ``a``.

    The seed is a pure SHA-256-derived 31-bit integer:

    ``candidate_seed(i, a) = reduce31(sha256(base_seed | protocol | profile | i | a | role))``

    It depends only on its own ``(i, a)`` and the resolved scientific identity,
    so:

    * same ``(i, a)`` → same seed;
    * a retry of ``i`` never consumes randomness belonging to another index;
    * increasing requested record count does not alter earlier indexes;
    * worker count / scheduling / enumeration order do not alter output.
    """
    if index < 0:
        raise GenerationError(f"logical topology index must be >= 0, got {index}")
    if attempt < 0:
        raise GenerationError(f"retry attempt must be >= 0, got {attempt}")
    material = "|".join(
        (
            str(configuration.seed),
            configuration.generator_protocol,
            configuration.generator_profile,
            str(index),
            str(attempt),
            configuration.randomness_role,
        )
    )
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], byteorder="big") & ((1 << _CANDIDATE_SEED_SPACE_BITS) - 1)


# ---------------------------------------------------------------------------
# Native invocation
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class NativeCandidate:
    """A raw native candidate from the frozen external generator.

    ``dungeon`` is the upstream structured ``Dungeon`` layout; ``cells`` is the
    faithful native occupancy raster ``{(x, y): cell_type int}`` populated
    during generation from rooms, passages, doors, stairs, and exits. Only the
    stable spatial mapping is exposed; native unstable room/door object IDs are
    deliberately not surfaced as public content.
    """

    dungeon: Any
    cells: dict[tuple[int, int], int]
    seed: int


def generate_native(configuration: DungeonGenConfiguration, seed: int) -> NativeCandidate:
    """Invoke the exact upstream generator for one candidate seed.

    Runs ``DungeonGenerator(to_upstream_params(profile)).generate(seed=seed)``
    over the frozen layout subsystem and returns the native candidate with its
    occupancy raster. Rendering subsystems are never invoked.
    """
    from dungeongen.layout.generator import DungeonGenerator

    params = to_upstream_params(configuration.profile)
    generator = DungeonGenerator(params)
    dungeon = generator.generate(seed=seed)
    cells = dict(generator.occupancy._cells)
    return NativeCandidate(dungeon=dungeon, cells=cells, seed=seed)


__all__ = [
    "GenerationError",
    "NativeCandidate",
    "candidate_seed",
    "generate_native",
    "to_upstream_params",
    "verify_dependency_build_ready",
]
