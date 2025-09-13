import sys
import threading
from collections import deque
from typing import Any

import numpy as np
import sounddevice as sd
from numpy import float32, float64
from numpy.typing import NDArray
from sounddevice import CallbackFlags

from olivia_modem.fec_codec import FECCodec
from olivia_modem.mode_parameters import ModeParameters
from olivia_modem.shared_types import SDSamples
from olivia_modem.tone_generator import ToneGenerator, ToneSamples

__all__ = ["Transmitter"]


class Transmitter:
    def __init__(
        self, parameters: ModeParameters, device: int | str, attenuation: float = 30.0
    ):
        self.sample_rate = parameters.sample_rate
        self.vector_length = parameters.vector_length
        self.symbol_len = parameters.symbol_len
        self.chars_per_block = parameters.chars_per_block

        self.tx_queue: deque[SDSamples] = deque()
        self.tx_block_len = self.symbol_len * self.vector_length
        self.tx_finished = threading.Event()
        self.tx_stream = sd.OutputStream(**self.get_tx_stream_kwargs(device))

        self.tone = ToneGenerator(parameters)
        self.fec = FECCodec(parameters)
        self.last_symbol: ToneSamples = np.zeros(self.symbol_len, dtype=float64)
        self.attenuation = float64(attenuation)

    def generate_block(
        self, chars: str, tail: ToneSamples
    ) -> tuple[ToneSamples, ToneSamples]:
        txlen = self.tx_block_len
        slen = self.symbol_len
        buff = np.zeros(txlen + slen, dtype=float64)

        # Overlap last symbol
        buff[0:slen] = tail

        symbols = self.fec.str_to_symbols(chars)
        for i, tone_number in enumerate(symbols):
            tone = self.tone.generate_tone(tone_number)
            start = slen * i
            buff[start : start + len(tone)] += tone

        return buff[:txlen], buff[txlen:]

    def enqueue_block(self, block: ToneSamples, pad_left: bool) -> None:
        txlen = self.tx_block_len
        inslen = len(block)
        padding = (txlen - inslen % txlen) % txlen
        if pad_left:
            pad_width = (padding, 0)
        else:
            pad_width = (0, padding)

        buff = np.pad(block, pad_width=pad_width, mode="constant")
        buff /= self.attenuation
        for i in range(0, len(buff), txlen):
            chunk = buff[i : i + txlen]
            self.tx_queue.append(chunk.astype(float32))

    def add_opening(self) -> None:
        preamble = self.tone.generate_preamble()
        self.enqueue_block(preamble, pad_left=True)

    def add_closing(self) -> None:
        closing = np.concatenate((self.last_symbol, self.tone.generate_preamble()))
        self.last_symbol.fill(0)
        self.enqueue_block(closing, pad_left=False)

    def add_message(self, message: str) -> None:
        tail = self.last_symbol
        cpb = self.chars_per_block
        for i in range(0, len(message), cpb):
            piece = message[i : i + cpb].ljust(cpb, "\0")
            block, tail = self.generate_block(piece, tail)
            self.enqueue_block(block, pad_left=False)

        self.last_symbol = tail

    def get_tx_stream_kwargs(self, device: int | str) -> dict[str, Any]:
        return {
            "device": device,
            "samplerate": self.sample_rate,
            "blocksize": self.tx_block_len,
            "channels": 1,
            "dtype": float32,
            "callback": self.sounddevice_tx_callback,
            "finished_callback": self.tx_finished.set,
        }

    def sounddevice_tx_callback(
        self,
        outdata: NDArray[Any],
        frames: int,
        time: Any,
        status: CallbackFlags,
    ) -> None:
        if status:
            print(status, file=sys.stderr)

        if self.tx_queue:
            outdata[:, 0] = self.tx_queue.popleft()
        else:
            raise sd.CallbackStop()

    def tx_start(self) -> None:
        self.tx_stream.start()
        self.tx_finished.clear()
        threading.Thread(target=self.tx_finished.wait).start()

    def tx_abort(self) -> None:
        self.tx_finished.set()
        self.tx_stream.stop()
        self.tx_queue.clear()
        self.last_symbol.fill(0)
