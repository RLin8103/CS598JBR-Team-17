import pytest
from HumanEval_4 import *

def test_example():
    assert abs(mean_absolute_deviation([1.0, 2.0, 3.0]) - 2.0 / 3.0) < 1e-06

def test_empty_list():
    assert mean_absolute_deviation([]) == 0

def test_single_element():
    assert mean_absolute_deviation([5]) == 0

def test_zero_values():
    assert mean_absolute_deviation([0, 0, 0, 0]) == 0

def test_negative_values():
    assert mean_absolute_deviation([-1, -2, -3, -4]) == -1

def test_boundary_values():
    assert mean_absolute_deviation([1000000.0, -1000000.0]) == 2000000.0

def test_large_dataset():
    numbers = list(range(1, 1000001))
    assert mean_absolute_deviation(numbers) == 500000.5

def test_negative_and_positive_values():
    assert mean_absolute_deviation([-1, 1, -2, 2]) == 1

def test_positive_values():
    assert mean_absolute_deviation([1, 2, 3, 4]) == 1

def test_negative_values():
    assert mean_absolute_deviation([-1, -2, -3, -4]) == 1

def test_zero_deviation():
    assert mean_absolute_deviation([1, 1, 1, 1]) == 0

def test_large_deviation():
    assert mean_absolute_deviation([1000000.0, 10000000.0]) == 5000000.0

def test_negative_large_deviation():
    assert mean_absolute_deviation([-1000000.0, -10000000.0]) == -5000000.0
