import math
from dataclasses import dataclass

from olivia_modem.functions import is_power_of_2

__all__ = ["ModeParameters"]


@dataclass()
class ModeParameters:
    symbols: int = 32
    bandwidth: int = 1000
    center_frequency: int = 1500
    sample_rate: int = 8000
    scramble_key: int = 0xE257E6D0291574EC
    vector_length: int = 64

    @property
    def symbol_spacing(self) -> float:
        """Frequency separation between symbols, in Hz."""
        return self.bandwidth / self.symbols

    @property
    def symbol_len(self) -> int:
        """Time separation between symbols, in samples."""
        return math.ceil(self.sample_rate / self.symbol_spacing)

    @property
    def chars_per_block(self) -> int:
        """Number of chars per block."""
        return math.floor(math.log2(self.symbols))

    @property
    def scramble_key_bits(self) -> list[int]:
        key_bits = []
        for bit_pos in range(self.vector_length):
            bit_value = (self.scramble_key >> bit_pos) & 1
            key_bits.append(bit_value)

        return key_bits

    def __post_init__(self) -> None:
        if not is_power_of_2(self.symbols):
            raise ValueError("Symbols must be a power of 2")
