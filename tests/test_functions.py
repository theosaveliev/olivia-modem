from olivia_modem.functions import bits_to_int, is_power_of_2


def test_is_power_of_2():
    assert is_power_of_2(32) is True


def test_bits_to_int():
    assert bits_to_int([1, 0, 0, 0, 0, 0]) == 32
