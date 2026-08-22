"""Root ``ehp-sn`` command assembly.

Owns only the root command surface: the command name, help text, and the
top-level command groups. Command groups are mounted here and implement their
own options and callbacks.

The root interface is defined by ``docs/docs/interfaces/cli/index.md``: only
``--help``, ``--version``, ``--install-completion``, and ``--show-completion``
are root-level. No operation orchestration lives here; callbacks delegate to
presentation-independent seams (CLI-001).
"""

from __future__ import annotations

from importlib import metadata

import typer

from ehp_sn.cli.data import app as data_app


def _version() -> str:
    """The installed ``ehp-sn`` package version.

    Sourced from installed package metadata (``importlib.metadata``) so the CLI
    and runtime report the same version. Falls back to ``0.0.0`` when the
    package is not importable as installed (e.g. running from a source tree).
    """
    try:
        return metadata.version("ehp-sn")
    except metadata.PackageNotFoundError:
        return "0.0.0"


app = typer.Typer(
    name="ehp-sn",
    help="EHP-SN research framework.",
    no_args_is_help=True,
    invoke_without_command=True,
)


@app.callback()
def _main(
    version: bool = typer.Option(False, "--version", help="Show the version and exit."),
) -> None:
    """The ``ehp-sn`` root command."""
    if version:
        typer.echo(f"ehp-sn {_version()}")
        raise typer.Exit()


app.add_typer(data_app, name="data")

