import pytest
from HumanEval_139 import *

def test_example():
    assert special_factorial(4) == 288, 'Test 4'

def test_zero():
    assert special_factorial(0) == 1, 'Test 0'

def test_negative():
    with pytest.raises(ValueError):
        special_factorial(-1)

def test_one():
    assert special_factorial(1) == 1, 'Test 1'

def test_two():
    assert special_factorial(2) == 2, 'Test 2'

def test_large_number():
    assert special_factorial(5) == 5 * 4 * 3 * 2 * 1, 'Test 5'

def test_large_number_2():
    assert special_factorial(6) == 6 * 5 * 4 * 3 * 2 * 1, 'Test 6'

def test_large_number_3():
    assert special_factorial(7) == 7 * 6 * 5 * 4 * 3 * 2 * 1, 'Test 7'

def test_large_number_4():
    assert special_factorial(8) == 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1, 'Test 8'

def test_large_number_5():
    assert special_factorial(9) == 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1, 'Test 9'

def test_large_number_6():
    assert special_factorial(10) == 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1, 'Test 10'

def test_large_number_7():
    assert special_factorial(11) == 11 * 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1, 'Test 11'

def test_large_number_8():
    assert special_factorial(12) == 12 * 11 * 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1, 'Test 12'

def test_large_number_9():
    assert special_factorial(13) == 13 * 12 * 11 * 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1, 'Test 13'

def test_large_number_10():
    assert special_factorial(14) == 14 * 13 * 12 * 11 * 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1, 'Test 14'

def test_large_number_11():
    assert special_factorial(15) == 15 * 14 * 13 * 12 * 11 * 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1, 'Test 15'
