"""The ``ehp-sn data`` command group.

Generates, validates, and inspects immutable interim substrates
(``docs/docs/interfaces/cli/data.md``).

This is deliberately a thin orchestration shell (CLI-001). The group's help
surface is specified and stable; the substrate operations themselves are not yet
implemented here. Their target-resolution and definition contract is still being
derived from a non-discoverable design exemplar (``ARCH-014``/``ARCH-016``), so
no operation subcommand is registered yet that would require establishing a
production substrate catalogue or ``SubstrateDefinition`` type. They will be
mounted here as their contracts are pressure-tested and specified.
"""

from __future__ import annotations

import typer

app = typer.Typer(
    help="Generate, validate, and inspect substrate artifacts.",
    no_args_is_help=True,
)
