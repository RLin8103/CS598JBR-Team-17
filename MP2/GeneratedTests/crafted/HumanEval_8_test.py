import pytest
from HumanEval_8 import *

def test_empty_list():
    assert sum_product([]) == (0, 1)

def test_single_element():
    assert sum_product([5]) == (5, 5)

def test_zero():
    assert sum_product([0, 0, 0]) == (0, 0)

def test_negative_numbers():
    assert sum_product([-1, -2, -3, -4]) == (-10, 24)

def test_positive_numbers():
    assert sum_product([1, 2, 3, 4]) == (10, 24)

def test_large_numbers():
    assert sum_product([100, 200, 300, 400]) == (1000, 2400000)

def test_negative_and_positive_numbers():
    assert sum_product([-1, 2, -3, 4]) == (-2, -24)

def test_boundary_values():
    assert sum_product([1000000, -1000000, 0]) == (0, 0)

def test_large_negative_numbers():
    assert sum_product([-1000000, -2000000, -3000000, -4000000]) == (-1000000, 24000000000000)

def test_large_positive_numbers():
    assert sum_product([1000000, 2000000, 3000000, 4000000]) == (10000000, 24000000000000)

def test_negative_and_large_numbers():
    assert sum_product([-1000000, 2000000, -3000000, 4000000]) == (-1000000, -24000000000000)

def test_positive_and_large_numbers():
    assert sum_product([1000000, 2000000, 3000000, 4000000]) == (10000000, 24000000000000)
