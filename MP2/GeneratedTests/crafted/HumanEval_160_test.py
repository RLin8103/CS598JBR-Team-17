import pytest
from HumanEval_160 import *

def test_example():
    assert do_algebra(['**', '*', '+'], [2, 3, 4, 5]) == 37

def test_addition():
    assert do_algebra(['+'], [2, 3]) == 5

def test_subtraction():
    assert do_algebra(['-'], [5, 3]) == 2

def test_multiplication():
    assert do_algebra(['*'], [2, 3]) == 6

def test_floor_division():
    assert do_algebra(['//'], [10, 3]) == 3

def test_exponentiation():
    assert do_algebra(['**'], [2, 3]) == 8

def test_multiple_operators():
    assert do_algebra(['+', '-', '*'], [2, 3, 4, 5]) == 11

def test_empty_input():
    with pytest.raises(IndexError):
        do_algebra([], [])

def test_single_element():
    with pytest.raises(IndexError):
        do_algebra(['+'], [2])

def test_zero_operand():
    assert do_algebra(['+'], [2, 0]) == 2

def test_negative_operand():
    assert do_algebra(['-'], [2, 3]) == -1

def test_negative_result():
    assert do_algebra(['*'], [-2, 3]) == -6

def test_boundary_values():
    assert do_algebra(['+'], [2 ** 31 - 1, 2 ** 31 - 1]) == 2 ** 31 - 1 + 2 ** 31 - 1

def test_large_numbers():
    assert do_algebra(['**'], [2, 10 ** 6]) == 2 ** 10 ** 6

def test_large_operands():
    assert do_algebra(['*'], [2 ** 31 - 1, 2 ** 31 - 1]) == 2 ** 60
