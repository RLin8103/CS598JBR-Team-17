import pytest
from HumanEval_105 import *

def test_example():
    assert by_length([2, 1, 1, 4, 5, 8, 2, 3]) == ['Eight', 'Five', 'Four', 'Three', 'Two', 'Two', 'One', 'One'], 'Error'

def test_empty_array():
    assert by_length([]) == [], 'Error'

def test_single_element():
    assert by_length([1]) == ['One'], 'Error'

def test_zero():
    assert by_length([0, 0, 0, 0]) == [], 'Error'

def test_negative_numbers():
    assert by_length([-1, -1, -1]) == [], 'Error'

def test_boundary_values():
    assert by_length([9, 9, 9, 9, 9, 9, 9, 9, 9, 9]) == ['Nine', 'Nine', 'Nine', 'Nine', 'Nine', 'Nine', 'Nine', 'Nine', 'Nine', 'Nine'], 'Error'

def test_mixed_positive_negative_numbers():
    assert by_length([1, -1, 55]) == ['Five', 'One'], 'Error'

def test_mixed_positive_negative_numbers_2():
    assert by_length([-1, 1, 55]) == ['Five', 'One'], 'Error'

def test_mixed_positive_negative_numbers_3():
    assert by_length([-1, -1, 55, 55]) == ['Five', 'Five'], 'Error'

def test_mixed_positive_negative_numbers_4():
    assert by_length([-1, -1, -1, 55, 55, 55]) == ['Five', 'Five', 'Five'], 'Error'

def test_mixed_positive_negative_numbers_5():
    assert by_length([-1, -1, -1, -1, 55, 55, 55, 55]) == ['Five', 'Five', 'Five', 'Five'], 'Error'

def test_mixed_positive_negative_numbers_6():
    assert by_length([-1, -1, -1, -1, -1, 55, 55, 55, 55, 55]) == ['Five', 'Five', 'Five', 'Five', 'Five'], 'Error'
