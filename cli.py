""" New console interface for the application using Typer. """
from dataclasses import fields, replace
from pathlib import Path
from typing import Any

import typer

from config.app_settings import AppSettings, read_app_settings
from main import main as run_analyzer

app = typer.Typer()
_TRUE_VALUES = {"1", "true", "yes", "y"}

def _coerce_value(current: Any, raw: str) -> Any:
    if isinstance(current, bool):
        return raw.lower() in _TRUE_VALUES
    if isinstance(current, Path):
        return Path(raw).expanduser()
    if isinstance(current, int):
        return int(raw)
    return type(current)(raw)

def _prompt_setting(settings: AppSettings, field_name: str) -> AppSettings:
    current = getattr(settings, field_name)
    response = typer.prompt(f"{field_name}", default=str(current))
    if response == str(current):
        return settings
    updated = _coerce_value(current, response)
    return replace(settings, **{field_name: updated})

@app.command()
def run() -> None:
    """ Run the campaign analyzer with interactive settings. """
    settings: AppSettings = read_app_settings()
    typer.echo("Loaded settings:\n")
    for field in fields(settings):
        typer.echo(f"  {field.name}: {getattr(settings, field.name)}")
    typer.echo()
    if typer.confirm("Modify any setting?", default=False):
        for field in fields(settings):
            settings = _prompt_setting(settings, field.name)
    typer.echo("\nFinal settings:")
    for field in fields(settings):
        typer.echo(f"  {field.name}: {getattr(settings, field.name)}")
    if not typer.confirm("\nProceed with these settings?", default=True):
        typer.echo("Aborted.")
        raise typer.Exit(code=1)
    run_analyzer(settings)

if __name__ == "__main__":
    app()
