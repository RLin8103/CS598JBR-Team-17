import pytest
from HumanEval_109 import *

def test_example():
    assert move_one_ball([3, 4, 5, 1, 2]) == True

def test_empty_array():
    assert move_one_ball([]) == True

def test_sorted_array():
    assert move_one_ball([1, 2, 3, 4, 5]) == True

def test_reverse_sorted_array():
    assert move_one_ball([5, 4, 3, 2, 1]) == True

def test_single_element_array():
    assert move_one_ball([1]) == True

def test_negative_numbers():
    assert move_one_ball([1, -2, -3]) == True

def test_zero():
    assert move_one_ball([0, 1, 2]) == True

def test_boundary_values():
    assert move_one_ball([100, 200, 300]) == True

def test_unsorted_array():
    assert move_one_ball([3, 5, 4, 1, 2]) == False

def test_unsorted_array_with_shift():
    assert move_one_ball([2, 3, 5, 4, 1]) == False

def test_unsorted_array_with_multiple_shifts():
    assert move_one_ball([1, 3, 2]) == True

def test_unsorted_array_with_negative_numbers():
    assert move_one_ball([1, -2, 3]) == True

def test_unsorted_array_with_zero():
    assert move_one_ball([1, 0, 2]) == True

def test_unsorted_array_with_boundary_values():
    assert move_one_ball([300, 200, 100]) == True
