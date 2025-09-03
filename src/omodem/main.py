from pathlib import Path

import click
import sounddevice as sd
import yaml

from olivia_modem import Receiver, Transmitter
from omodem.functions import inline_echo, read_preset_file

in_path = click.Path(
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    allow_dash=True,
    path_type=Path,
)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
DEFAULT_MIC = sd.default.device[0]
DEFAULT_SPK = sd.default.device[1]


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(package_name="olivia-modem")
def cli() -> None:
    pass


@cli.command()
@click.option("--preset-file", default="presets.yaml", show_default=True, type=in_path)
def info_cmd(preset_file: Path) -> None:
    """Print information about audio devices and OMFSK presets."""
    click.echo("Audio devices:")
    click.echo(sd.query_devices())

    _, pd = read_preset_file(preset_file)
    info = {"Presets": pd}
    click.echo(yaml.safe_dump(info, sort_keys=False))


@cli.command()
@click.argument("message_file", default="-", type=in_path)
@click.option("--pad", is_flag=True, default=False, help="Pad with line breaks.")
@click.option("--preset", "-p", default="64/2k", show_default=True)
@click.option("--device", "-d", default=DEFAULT_SPK, show_default=True, type=click.INT)
@click.option("--attenuation", default="5.0", show_default=True, type=click.FLOAT)
@click.option("--preset-file", default="presets.yaml", show_default=True, type=in_path)
def tx_cmd(
    message_file: Path,
    pad: bool,
    preset: str,
    device: int,
    attenuation: float,
    preset_file: Path,
) -> None:
    """Transmit a message."""
    presets, _ = read_preset_file(preset_file)
    settings = presets[preset]

    with click.open_file(message_file) as fd:
        message = fd.read()

    if not message.isascii():
        raise ValueError("Non-ASCII characters in the message")

    trans = Transmitter(settings=settings, device=device, attenuation=attenuation)
    trans.add_opening()
    if pad:
        trans.add_message("\n" * settings.chars_per_block)

    trans.add_message(message)
    if pad:
        trans.add_message("\n" * settings.chars_per_block)

    trans.add_closing()
    trans.tx_start()


@cli.command()
@click.option("--preset", "-p", default="64/2k", show_default=True)
@click.option("--device", "-d", default=DEFAULT_MIC, show_default=True, type=click.INT)
@click.option("--confidence", default="24.0", show_default=True, type=click.FLOAT)
@click.option("--preset-file", default="presets.yaml", show_default=True, type=in_path)
def rx_cmd(preset: str, device: int, confidence: float, preset_file: Path) -> None:
    """Receive a message."""
    presets, _ = read_preset_file(preset_file)
    settings = presets[preset]

    recv = Receiver(
        settings=settings, device=device, confidence=confidence, callback=inline_echo
    )

    recv.rx_start()


if __name__ == "__main__":
    cli()
