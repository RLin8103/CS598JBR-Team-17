import pytest
from HumanEval_85 import *

def test_empty_list():
    assert add([]) == 0

def test_single_element():
    assert add([5]) == 0

def test_zero():
    assert add([0, 1, 2, 0, 3]) == 2

def test_negative_numbers():
    assert add([-1, 2, -3, 4]) == -2

def test_odd_indices():
    assert add([1, 2, 3, 4, 5]) == 9

def test_even_numbers():
    assert add([1, 2, 3, 4, 5]) == 6

def test_even_numbers_at_odd_indices():
    assert add([1, 2, 3, 4, 5, 6]) == 12

def test_even_numbers_at_even_indices():
    assert add([2, 1, 4, 1, 6, 1]) == 8

def test_large_numbers():
    assert add([100, 200, 300, 400, 500]) == 600

def test_negative_large_numbers():
    assert add([-100, -200, -300, -400, -500]) == -600

def test_mixed_positive_negative_numbers():
    assert add([100, -200, 300, -400, 500]) == 200

def test_floats():
    assert add([1.5, 2.5, 3.5, 4.5, 5.5]) == pytest.approx(16.5)

def test_negative_floats():
    assert add([-1.5, -2.5, -3.5, -4.5, -5.5]) == pytest.approx(-16.5)

def test_mixed_positive_negative_floats():
    assert add([1.5, -2.5, 3.5, -4.5, 5.5]) == pytest.approx(3.5)
