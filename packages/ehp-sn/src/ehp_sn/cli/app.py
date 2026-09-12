from __future__ import annotations

from importlib import metadata
from pathlib import Path
from typing import Annotated

import typer

from ehp_sn.cli.data import app as data_app
from ehp_sn.cli.tasks import app as tasks_app


def _version() -> str:
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
    experiment: Annotated[
        Path | None,
        typer.Option("--experiment", help="Path to the experiment configuration file."),
    ] = None,
    version: Annotated[
        bool,
        typer.Option("--version", help="Show the version and exit."),
    ] = False,
) -> None: ...


app.add_typer(data_app, name="data")
app.add_typer(tasks_app, name="tasks")
