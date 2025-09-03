# olivia-modem

Olivia MFSK modem.

This is a fork of: https://github.com/sntfrc/olivia-python

The original work can be found in the [original](original) dir.
I refactored the project as a lib to use in my hobby projects.


#### Installation

1. Install [PortAudio](https://portaudio.com/)
   and [uv](https://docs.astral.sh/uv/getting-started/installation/)
   ```
   % apt install libportaudio2
   % apt install pipx
   % pipx install uv
   ```
2. Install the olivia-modem
   ```
   % uv sync --extra cli
   % uv tool install '.[cli]'
   ```
3. Uninstall the olivia-modem
   ```
   % uv tool uninstall olivia-modem
   ```


#### Getting help

All commands have the `[-h | --help]` option:
```
% omodem -h
Usage: omodem [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  info  Print information about audio devices and OMFSK presets.
  rx    Receive a message.
  tx    Transmit a message.
```


#### Sending a message

```
% echo qwerty | omodem tx -

% omodem tx -h
Usage: omodem tx [OPTIONS] [MESSAGE_FILE]

  Transmit a message.

Options:
  --pad                 Pad with line breaks.
  -p, --preset TEXT     [default: 64/2k]
  -d, --device INTEGER  [default: 1]
  --attenuation FLOAT   [default: 5.0]
  --preset-file FILE    [default: presets.yaml]
  -h, --help            Show this message and exit.
```


#### Receiving a message

```
% omodem rx

% omodem rx -h
Usage: omodem rx [OPTIONS]

  Receive a message.

Options:
  -p, --preset TEXT     [default: 64/2k]
  -d, --device INTEGER  [default: 0]
  --confidence FLOAT    [default: 24.0]
  --preset-file FILE    [default: presets.yaml]
  -h, --help            Show this message and exit.
```
