from typing import Iterable

__all__ = ["is_power_of_2", "bits_to_int"]


def is_power_of_2(n: int) -> bool:
    return n > 0 and n & (n - 1) == 0


def bits_to_int(data: Iterable[int]) -> int:
    return int("".join(str(x) for x in data), 2)
