import pytest

from olivia_modem.mode_parameters import ModeParameters


@pytest.fixture
def parameters():
    """Modulation parameters."""
    return ModeParameters(
        symbols=64,
        bandwidth=2000,
        center_frequency=1500,
        sample_rate=8000,
        scramble_key=0xE257E6D0291574EC,
        vector_length=64,
    )
