from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ehp_sn import discovery
from ehp_sn.tasks import *

app = typer.Typer(
    help="Build, validate, and inspect processed task corpora.",
    no_args_is_help=True,
    rich_markup_mode=None,
)


@app.command("list")
def list_command(
    format: Annotated[
        str,
        typer.Option("--format", help="Output format: text|json"),
    ] = "text",
) -> None: ...


@app.command()
def show_command(
    target: Annotated[
        str,
        typer.Argument(help="Task family reference, e.g. task:maze-hard/v1"),
    ],
    format: Annotated[
        str,
        typer.Option("--format", help="Output format: text|json"),
    ] = "text",
) -> None: ...


@app.command()
def plan(
    target: Annotated[
        str,
        typer.Argument(help="Task family reference, e.g. task:maze-hard/v1"),
    ],
    config: Annotated[
        str,
        typer.Option("--config", help="Task configuration file"),
    ],
    release: Annotated[
        int | None,
        typer.Option("--release", help="Corpus release number."),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", help="Output format: text|json"),
    ] = "text",
    seed: Annotated[
        int,
        typer.Option("--seed", help="Deterministic generation seed."),
    ] = 0,
) -> None: ...


@app.command("build")
def build_command(
    target: Annotated[
        str,
        typer.Argument(help="Task family reference."),
    ],
    config: Annotated[
        str,
        typer.Option("--config", help="Generation configuration file."),
    ],
    release: Annotated[
        int | None,
        typer.Option("--release", help="Corpus release number."),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", help="Output format: text|json"),
    ] = "text",
    seed: Annotated[
        int,
        typer.Option("--seed", help="Deterministic generation seed."),
    ] = 0,
) -> None: ...


@app.command("validate")
def validate_command(
    artifact: Annotated[
        str,
        typer.Argument(help="Path or artifact reference."),
    ],
    level: Annotated[
        str,
        typer.Option("--level", help="Validation depth (quick|full)."),
    ] = "full",
    format: Annotated[
        str,
        typer.Option("--format", help="Output format: text|json"),
    ] = "text",
) -> None: ...


@app.command("summarize")
def summarize_command(
    artifact: Annotated[
        str,
        typer.Argument(help="Path or artifact reference."),
    ],
    samples: Annotated[
        int,
        typer.Option("--samples", help="Number of representative records."),
    ] = 0,
    show_figure: Annotated[
        bool,
        typer.Option(help="Display the inspection figure interactively."),
    ] = False,
    save_figure: Annotated[
        Path | None,
        typer.Option(help="Save the inspection figure to this path."),
    ] = None,
    format: Annotated[
        str,
        typer.Option(help="Output format: text|json."),
    ] = "text",
) -> None: ...


@app.command("inspect")
def inspect_command(
    artifact: Annotated[
        str,
        typer.Argument(help="Path or artifact reference."),
    ],
    record_id: Annotated[
        str,
        typer.Argument(help="Record identifier."),
    ],
    show_figure: Annotated[
        bool,
        typer.Option(help="Display the inspection figure interactively."),
    ] = False,
    save_figure: Annotated[
        Path | None,
        typer.Option(help="Save the inspection figure to this path."),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", help="Output format: text|json"),
    ] = "text",
) -> None: ...


__all__ = ["app"]
