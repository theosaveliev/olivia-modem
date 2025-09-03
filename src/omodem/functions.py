from pathlib import Path
from typing import Any

import click
import yaml

from olivia_modem import BaseSettings

__all__ = ["read_preset_file", "inline_echo"]


def read_preset_file(src: Path) -> tuple[dict[str, BaseSettings], dict[str, Any]]:
    with click.open_file(src) as fd:
        original = yaml.safe_load(fd.read())

    parsed = {}
    for name, settings in original.items():
        args = settings.copy()
        args["scramble_key"] = int(args["scramble_key"], base=16)
        parsed[name] = BaseSettings(**args)

    return parsed, original


def inline_echo(message: str) -> None:
    click.echo(message, nl=False)
