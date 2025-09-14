# pylint: disable=redefined-outer-name
# ruff: noqa: F811
import numpy as np
import pytest
from numpy import float64

from olivia_modem.tone_generator import ToneGenerator

from .fixtures import parameters  # noqa: F401 pylint: disable=unused-import


@pytest.fixture
def tone(parameters):
    return ToneGenerator(parameters)


@pytest.fixture
def samples():
    """Random tone samples."""
    return np.ones(10, dtype=float64)


@pytest.fixture
def shaped():
    """Shaped tone samples."""
    value = (
        "-0.05498883 -0.03362665 0.75795379 1.85321072 1.94995656 1.94995656 "
        "1.85321072 0.75795379 -0.03362665 -0.05498883"
    )
    return np.fromstring(value, sep=" ")


def test_get_freq(tone):
    assert tone.get_freq(0) == 515.625


def test_get_tone_samples(tone):
    assert len(tone.get_tone_samples(500.0)) == 512


def test_get_preamble_samples(tone):
    assert len(tone.get_preamble_samples(500.0)) == 2000


def test_shape_tone(tone, samples, shaped):
    assert np.isclose(tone.shape_tone(samples), shaped).all()


def test_generate_tone(tone):
    assert len(tone.generate_tone(0)) == 512


def test_generate_preamble(tone):
    assert len(tone.generate_preamble()) == 8000
