import numpy as np
from numpy import int8
from numpy.typing import NDArray

from olivia_modem.functions import bits_to_int
from olivia_modem.mode_parameters import ModeParameters

__all__ = ["FECCodec", "Vector"]

# A list of [-1,1] values of vector_length
type Vector = NDArray[int8]


class FECCodec:
    def __init__(self, parameters: ModeParameters):
        self.vector_length = parameters.vector_length
        self.symbol_len = parameters.symbol_len
        self.chars_per_block = parameters.chars_per_block
        self.scramble_key_bits = parameters.scramble_key_bits

    def char_to_vector(self, char: str) -> Vector:
        vlen = self.vector_length
        vector = np.zeros(vlen, dtype=int8)
        code = ord(char)
        if code > vlen * 2:
            raise ValueError(f"Char code {code} cannot be encoded in {vlen} bits")

        if code < vlen:
            vector[code] = 1
        else:
            vector[code - vlen] = -1

        return vector

    def vector_to_char(self, vector: Vector, confidence: float) -> str | None:
        # Find character index
        code = int(np.argmax(np.abs(vector)))
        if abs(vector[code]) < confidence:
            return None

        if vector[code] < 0:
            code += self.vector_length

        return chr(code)

    @staticmethod
    def fwht(char: Vector) -> Vector:
        """Fast Walsh-Hadamard Transform (FWHT)."""
        char = char.copy()
        step = 1
        while step < len(char):
            for ptr in range(0, len(char), 2 * step):
                for ptr2 in range(ptr, ptr + step):
                    bit1 = char[ptr2]
                    bit2 = char[ptr2 + step]

                    char[ptr2] = bit1 + bit2
                    char[ptr2 + step] = bit2 - bit1

            step *= 2
        return char

    @staticmethod
    def ifwht(char: Vector) -> Vector:
        """Inverse Fast Walsh-Hadamard Transform (IFWHT)."""
        char = char.copy()
        step = len(char) // 2
        while step >= 1:
            for ptr in range(0, len(char), 2 * step):
                for ptr2 in range(ptr, ptr + step):
                    bit1 = char[ptr2]
                    bit2 = char[ptr2 + step]

                    char[ptr2] = bit1 - bit2
                    char[ptr2 + step] = bit1 + bit2

            step //= 2
        return char

    def scramble(self, char: Vector, rotate: int) -> Vector:
        """Scrambler encoding/decoding."""
        result = char.copy()
        code_wrap = len(self.scramble_key_bits) - 1
        code_bit = (13 * rotate) & code_wrap
        for time_bit in range(len(char)):
            if self.scramble_key_bits[code_bit] == 1:
                result[time_bit] = -result[time_bit]

            code_bit = (code_bit + 1) & code_wrap
        return result

    @staticmethod
    def gray_encode(n: int) -> int:
        """Gray encode."""
        return n ^ (n >> 1)

    @staticmethod
    def gray_decode(n: int) -> int:
        """Gray decode."""
        mask = n
        while mask != 0:
            mask >>= 1
            n ^= mask

        return n

    def str_to_symbols(self, chars: str) -> list[int]:
        """Transform a string into a list of tone numbers."""
        char_vectors = []
        for i, char in enumerate(chars):
            vector = self.char_to_vector(char)
            vector = self.ifwht(vector)
            vector = self.scramble(vector, i)
            char_vectors.append(vector)

        # Interleaving
        blen = len(char_vectors)
        vlen = self.vector_length
        symbols = []
        for j in range(vlen):
            row = np.zeros(blen, dtype=int8)
            for i in range(blen):
                q = (100 * blen + i - j) % blen
                if char_vectors[q][j] < 0:
                    row[i] = 1
            symbols.append(row)

        result = []
        for row in symbols:
            snum = bits_to_int(np.flip(row))
            snum = self.gray_encode(snum)
            result.append(snum)

        return result

    def symbols_to_str(self, block: list[int], confidence: float) -> tuple[str, int]:
        """Transform the tone numbers to the str."""
        decoded_symbols = [self.gray_decode(symbol) for symbol in block]

        # Deinterleaving
        blen = self.chars_per_block
        vlen = len(decoded_symbols)
        vectors = []
        for i in range(blen):
            row = np.zeros(vlen, dtype=int8)
            for j in range(vlen):
                # Extract bit at position ((i+j) % blen)
                q = (decoded_symbols[j] >> ((i + j) % blen)) & 1
                row[j] = -1 if q == 1 else 1
            vectors.append(row)

        decoding_errors = 0
        result = []
        for i, vector in enumerate(vectors):
            vector = self.scramble(vector, i)
            vector = self.fwht(vector)
            char = self.vector_to_char(vector, confidence)
            if char is None:
                decoding_errors += 1
            else:
                result.append(char)

        return "".join(result), decoding_errors
