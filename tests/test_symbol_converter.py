# pylint: disable=redefined-outer-name
import numpy as np
import pytest
from numpy import int8

from olivia_modem.base_settings import BaseSettings
from olivia_modem.symbol_converter import SymbolConverter


@pytest.fixture
def settings():
    """Modulation settings."""
    return BaseSettings(
        symbols=64,
        bandwidth=2000,
        center_frequency=1500,
        sample_rate=8000,
        scramble_key=0xE257E6D0291574EC,
        vector_length=64,
    )


@pytest.fixture
def symbol(settings):
    return SymbolConverter(settings=settings)


@pytest.fixture
def vector(settings):
    """A vector corresponding to the letter A."""
    result = np.zeros(settings.vector_length, dtype=int8)
    result[1] = -1
    return result


@pytest.fixture
def vector_ifwht():
    """IFWHT applied to the vector."""
    return np.fromstring("1 -1 " * 32, sep=" ", dtype=int8)


@pytest.fixture
def vector_fwht():
    """FWHT applied to the vector."""
    value = (
        "-1 -1 1 1 1 1 -1 -1 1 1 -1 -1 -1 -1 1 1 1 1 -1 -1 -1 -1 1 1 -1 -1 1 1 1 1 "
        "-1 -1 1 1 -1 -1 -1 -1 1 1 -1 -1 1 1 1 1 -1 -1 -1 -1 1 1 1 1 -1 -1 1 1 -1 "
        "-1 -1 -1 1 1"
    )
    return np.fromstring(value, sep=" ", dtype=int8)


@pytest.fixture
def vector_scrambled(vector):
    """The vector scrambled by key with rotate=1."""
    return vector * -1


@pytest.fixture
def symbol_block():
    """A block of symbols that contains AAAAAA."""
    value = (
        "23 43 52 5 12 5 61 61 48 36 28 51 55 54 11 20 41 52 21 29 30 16 4 60 19 "
        "22 22 45 56 17 20 52 61 56 48 60 28 51 53 54 13 0 1 52 23 27 20 8 44 60 "
        "19 21 26 53 16 32 23 55 55 44 40 12 28 53"
    )
    return list(map(int, value.split()))


@pytest.fixture
def symbol_block_ndarray(symbol_block):
    """A block of symbols that contains AAAAAA."""
    return np.asarray(symbol_block, dtype=int8)


def test_char_to_vector(symbol, vector):
    assert np.array_equal(symbol.char_to_vector("A"), vector)


def test_vector_to_char(symbol, vector):
    assert symbol.vector_to_char(vector, confidence=1.0) == "A"


def test_ifwht(symbol, vector, vector_ifwht):
    assert np.array_equal(symbol.ifwht(vector), vector_ifwht)


def test_fwht(symbol, vector, vector_fwht):
    assert np.array_equal(symbol.fwht(vector), vector_fwht)


def test_scramble(symbol, vector, vector_scrambled):
    assert np.array_equal(symbol.scramble(vector, 1), vector_scrambled)


def test_gray_encode(symbol):
    assert symbol.gray_encode(100) == 86


def test_gray_decode(symbol):
    assert symbol.gray_decode(100) == 71


def test_str_to_symbols(symbol, symbol_block_ndarray):
    assert np.array_equal(symbol.str_to_symbols("AAAAAA"), symbol_block_ndarray)


def test_symbols_to_str(symbol, symbol_block):
    decoded, errors = symbol.symbols_to_str(symbol_block, 1.0)
    assert decoded == "AAAAAA"
    assert errors == 0
