import pytest
from HumanEval_42 import *

def test_incr_list_empty():
    assert incr_list([]) == []

def test_incr_list_single_element():
    assert incr_list([1]) == [2]

def test_incr_list_multiple_elements():
    assert incr_list([1, 2, 3]) == [2, 3, 4]

def test_incr_list_negative_elements():
    assert incr_list([-1, 0, 1]) == [0, 1, 2]
