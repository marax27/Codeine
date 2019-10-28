import pytest


def test_nameOfTestedUnit_doNothing_pass():
    assert True


def test_nameOfTestedUnit_divideByZero_raiseZeroDivisionError():
    with pytest.raises(ZeroDivisionError):
        _ = 1 / 0
