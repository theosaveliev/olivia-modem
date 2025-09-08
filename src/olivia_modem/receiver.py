import sys
import threading
from collections import deque
from typing import Any, Callable

import sounddevice as sd
from numpy import float32
from numpy.typing import NDArray
from sounddevice import CallbackFlags

from olivia_modem.fec_codec import FECCodec, SDSamples
from olivia_modem.mode_parameters import ModeParameters
from olivia_modem.tone_generator import ToneGenerator

__all__ = ["Receiver"]


class Receiver:
    def __init__(
        self,
        parameters: ModeParameters,
        callback: Callable[[str], None],
        device: int | str,
        confidence: float = 24.0,
    ):
        self.sample_rate = parameters.sample_rate
        self.vector_length = parameters.vector_length
        self.symbol_len = parameters.symbol_len

        self.rx_queue: deque[int] = deque()
        self.rx_finished = threading.Event()
        self.rx_stream = sd.InputStream(**self.get_rx_stream_kwargs(device))

        self.tone = ToneGenerator(parameters)
        self.fec = FECCodec(parameters)
        self.confidence = confidence
        self.callback = callback

    def decode_block(self) -> None:
        vlen = self.vector_length
        if len(self.rx_queue) < vlen:
            return

        block = list(self.rx_queue)
        decoded, errors = self.fec.symbols_to_str(block[:vlen], self.confidence)
        if errors == 0:
            decoded = decoded.replace("\x00", "")
            self.callback(decoded)
            for _ in range(vlen):
                self.rx_queue.popleft()
        else:
            self.rx_queue.popleft()

    def identify_symbol(self, sample: SDSamples) -> int:
        base_freq = self.tone.get_freq(0)
        return self.fec.identify_symbol(sample, base_freq)

    def get_rx_stream_kwargs(self, device: int | str) -> dict[str, Any]:
        return {
            "device": device,
            "samplerate": self.sample_rate,
            "blocksize": self.symbol_len,
            "channels": 1,
            "dtype": float32,
            "callback": self.sounddevice_rx_callback,
            "finished_callback": self.rx_finished.set,
        }

    def sounddevice_rx_callback(
        self,
        indata: NDArray[Any],
        frames: int,
        time: Any,
        status: CallbackFlags,
    ) -> None:
        if status:
            print(status, file=sys.stderr)

        self.rx_queue.append(self.identify_symbol(indata[:, 0]))
        self.decode_block()

    def rx_start(self) -> None:
        self.rx_stream.start()
        self.rx_finished.clear()
        threading.Thread(target=self.rx_finished.wait).start()

    def rx_stop(self) -> None:
        self.rx_stream.stop()
        self.rx_finished.set()
        self.rx_queue.clear()
