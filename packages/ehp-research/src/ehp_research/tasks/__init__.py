"""Reusable scientific task definitions (``ehp_research.tasks``).

This package owns reusable scientific task meaning for ``ehp_research``
(``docs/authority.md``): each concrete task family's specification, builder,
validator, and scientific invariants. Task construction, validation, provenance,
and figures are reached through the generic framework task layer via each
registered definition — never through task-name branching in generic
orchestration.
"""

from __future__ import annotations

from .mazehard import (
    MAZEHARD_DEFINITION,
    MazeHardBuilder,
    MazeHardCase,
    MazeHardCorpus,
    MazeHardCorpusValidator,
    MazeHardDefinition,
    MazeHardValidation,
    validate_case,
)

#: All reusable task definitions this package admits to the generic catalogue.
TASK_DEFINITIONS = (MAZEHARD_DEFINITION,)

__all__ = [
    "MAZEHARD_DEFINITION",
    "MazeHardBuilder",
    "MazeHardCase",
    "MazeHardCorpus",
    "MazeHardCorpusValidator",
    "MazeHardDefinition",
    "MazeHardValidation",
    "TASK_DEFINITIONS",
    "validate_case",
]
