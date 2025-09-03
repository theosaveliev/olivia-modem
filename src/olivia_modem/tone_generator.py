import numpy as np
from numpy import float64, pi
from numpy.typing import NDArray

from olivia_modem.base_settings import BaseSettings

__all__ = ["ToneGenerator", "ToneSamples"]

# Generated audio samples
type ToneSamples = NDArray[float64]


class ToneGenerator:
    def __init__(self, settings: BaseSettings):
        self.symbols = settings.symbols
        self.bandwidth = settings.bandwidth
        self.center_frequency = settings.center_frequency
        self.sample_rate = settings.sample_rate
        self.symbol_spacing = settings.symbol_spacing

    def get_freq(self, tone_number: int) -> float:
        return (
            self.center_frequency
            - self.bandwidth / 2
            + self.symbol_spacing / 2
            + self.symbol_spacing * tone_number
        )

    def get_tone_samples(self, tone_freq: float) -> ToneSamples:
        tone_len = 2 / self.symbol_spacing
        samples = np.arange(0, tone_len, 1 / self.sample_rate)
        phase_shift = np.random.choice([-pi / 2, pi / 2])
        tone = np.sin(2 * pi * tone_freq * samples + phase_shift)
        return np.array(tone, dtype=float64)

    def get_preamble_samples(self, tone_freq: float) -> ToneSamples:
        tone_len = 1 / 4
        samples = np.arange(0, tone_len, 1 / self.sample_rate)
        tone = np.sin(2 * pi * tone_freq * samples)
        return np.array(tone, dtype=float64)

    @staticmethod
    def shape_tone(tone: ToneSamples) -> ToneSamples:
        """Shape tone to limit intersymbol modulation."""
        points = np.linspace(-pi, pi, len(tone))
        shape = (
            1.0
            + 1.1913785723 * np.cos(points)
            - 0.0793018558 * np.cos(2 * points)
            - 0.2171442026 * np.cos(3 * points)
            - 0.0014526076 * np.cos(4 * points)
        )

        return (tone * shape).astype(float64)

    def generate_tone(self, tone_number: int) -> ToneSamples:
        freq = self.get_freq(tone_number)
        samples = self.get_tone_samples(freq)
        return self.shape_tone(samples)

    def generate_preamble(self) -> ToneSamples:
        """First tone, last tone, first tone, last tone, each lasting 1/4 seconds."""
        first_freq = self.get_freq(0)
        last_freq = self.get_freq(self.symbols - 1)
        first_samples = self.get_preamble_samples(first_freq)
        last_samples = self.get_preamble_samples(last_freq)
        first_tone = self.shape_tone(first_samples)
        last_tone = self.shape_tone(last_samples)
        return np.concatenate((first_tone, last_tone, first_tone, last_tone))
