import pytest
from HumanEval_42 import *

def test_empty_list():
    assert incr_list([]) == []

def test_single_element():
    assert incr_list([0]) == [1]
    assert incr_list([-1]) == [0]
    assert incr_list([1]) == [2]

def test_multiple_elements():
    assert incr_list([1, 2, 3]) == [2, 3, 4]
    assert incr_list([-1, -2, -3]) == [0, -1, -2]
    assert incr_list([0, 0, 0]) == [1, 1, 1]

def test_large_numbers():
    assert incr_list([100, 200, 300]) == [101, 201, 301]
    assert incr_list([-100, -200, -300]) == [-99, -199, -299]

def test_boundary_values():
    assert incr_list([9999999999999999, 18446744073709551615]) == [10000000000000000, 18446744073709551616]
    assert incr_list([-9999999999999999, -18446744073709551615]) == [-9999999999999998, -18446744073709551614]

def test_float_numbers():
    assert incr_list([1.5, 2.5, 3.5]) == [2.5, 3.5, 4.5]
    assert incr_list([-1.5, -2.5, -3.5]) == [-0.5, -1.5, -2.5]
    assert incr_list([0.0, 0.0, 0.0]) == [1.0, 1.0, 1.0]

def test_non_integer_numbers():
    assert incr_list([1.1, 2.2, 3.3]) == pytest.approx([2.1, 3.2, 4.3])
    assert incr_list([-1.1, -2.2, -3.3]) == pytest.approx([-0.1, -1.2, -2.3])
    assert incr_list([0.0, 0.0, 0.0]) == [1.0, 1.0, 1.0]
