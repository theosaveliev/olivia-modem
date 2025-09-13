from numpy import float32
from numpy.typing import NDArray

__all__ = ["SDSamples"]

# Raw input/output from the audio device
type SDSamples = NDArray[float32]
