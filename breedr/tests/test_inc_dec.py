import pytest

from ask_data.inc_dec import increment, decrement


def test_increment():
    assert increment(0) == 1
    assert increment(1) == 2
    assert increment(-1) == 0

def test_decrement():
    assert decrement(0) == -1
    assert decrement(1) == 0
    assert decrement(-1) == -2
