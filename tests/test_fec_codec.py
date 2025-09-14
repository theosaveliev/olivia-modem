# pylint: disable=redefined-outer-name
import numpy as np
import pytest
from numpy import int8

from olivia_modem.fec_codec import FECCodec

from .fixtures import parameters  # noqa: F401 pylint: disable=unused-import


@pytest.fixture
def fec(parameters):  # noqa: F811
    return FECCodec(parameters)


@pytest.fixture
def vector():  # noqa: F811
    """A vector corresponding to the letter A."""
    value = (
        "0 -1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 "
        "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
    )

    return np.fromstring(value, sep=" ", dtype=int8)


@pytest.fixture
def vector_fwht():
    """FWHT applied to the vector."""
    value = (
        "-1 -1 1 1 1 1 -1 -1 1 1 -1 -1 -1 -1 1 1 1 1 -1 -1 -1 -1 1 1 -1 -1 1 1 1 1 -1 "
        "-1 1 1 -1 -1 -1 -1 1 1 -1 -1 1 1 1 1 -1 -1 -1 -1 1 1 1 1 -1 -1 1 1 -1 -1 -1 "
        "-1 1 1"
    )

    return np.fromstring(value, sep=" ", dtype=int8)


@pytest.fixture
def vector_ifwht():
    """IFWHT applied to the vector."""
    value = (
        "1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 "
        "-1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 1 -1 "
        "1 -1 "
    )

    return np.fromstring(value, sep=" ", dtype=int8)


@pytest.fixture
def vector_ifwht_scrambled():
    """The vector_ifwht scrambled with code_offset=1."""
    value = (
        "-1 1 1 1 1 1 1 1 1 -1 1 1 1 -1 -1 -1 -1 -1 1 -1 1 -1 1 1 1 1 -1 -1 -1 1 1 -1 "
        "-1 1 -1 1 -1 1 1 1 1 1 1 -1 -1 -1 1 -1 -1 1 -1 -1 1 1 -1 -1 -1 1 -1 -1 1 1 1 1"
    )

    return np.fromstring(value, sep=" ", dtype=int8)


@pytest.fixture
def symbol_block():
    """A block of symbols that contains AAAAAA."""
    value = (
        "23 43 52 5 12 5 61 61 48 36 28 51 55 54 11 20 41 52 21 29 30 16 4 60 19 22 22 "
        "45 56 17 20 52 61 56 48 60 28 51 53 54 13 0 1 52 23 27 20 8 44 60 19 21 26 53 "
        "16 32 23 55 55 44 40 12 28 53"
    )

    return list(map(int, value.split()))


def test_char_to_vector(fec, vector):
    assert np.array_equal(fec.char_to_vector("A"), vector)


def test_vector_to_char(fec, vector):
    assert fec.vector_to_char(vector, confidence=1.0) == "A"


def test_fwht(fec, vector, vector_fwht):
    assert np.array_equal(fec.fwht(vector), vector_fwht)


def test_ifwht(fec, vector, vector_ifwht):
    assert np.array_equal(fec.ifwht(vector), vector_ifwht)


def test_scramble(fec, vector_ifwht, vector_ifwht_scrambled):
    scrambled = fec.scramble(vector_ifwht, code_offset=1)
    assert np.array_equal(scrambled, vector_ifwht_scrambled)
    unscrambled = fec.scramble(scrambled, code_offset=1)
    assert np.array_equal(unscrambled, vector_ifwht)


def test_gray_encode(fec):
    assert fec.gray_encode(100) == 86


def test_gray_decode(fec):
    assert fec.gray_decode(100) == 71


def test_str_to_symbols(fec, symbol_block):
    assert np.array_equal(fec.str_to_symbols("AAAAAA"), symbol_block)


def test_symbols_to_str(fec, symbol_block):
    decoded, errors = fec.symbols_to_str(symbol_block, confidence=1.0)
    assert decoded == "AAAAAA"
    assert errors == 0
