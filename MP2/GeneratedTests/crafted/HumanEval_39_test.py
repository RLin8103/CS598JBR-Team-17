import pytest
from HumanEval_39 import *

def test_example():
    assert prime_fib(1) == 2

def test_second_fibonacci_prime():
    assert prime_fib(2) == 3

def test_third_fibonacci_prime():
    assert prime_fib(3) == 5

def test_fourth_fibonacci_prime():
    assert prime_fib(4) == 13

def test_fifth_fibonacci_prime():
    assert prime_fib(5) == 89

def test_sixth_fibonacci_prime():
    assert prime_fib(6) == 233

def test_seventh_fibonacci_prime():
    assert prime_fib(7) == 1597

def test_eighth_fibonacci_prime():
    assert prime_fib(8) == 28657

def test_ninth_fibonacci_prime():
    assert prime_fib(9) == 514229

def test_tenth_fibonacci_prime():
    assert prime_fib(10) == 144

def test_negative_input():
    with pytest.raises(ValueError):
        prime_fib(-1)

def test_zero_input():
    with pytest.raises(ValueError):
        prime_fib(0)

def test_large_input():
    assert prime_fib(100) == 8870976

def test_edge_case_single_digit_prime():
    assert prime_fib(1) == 2

def test_edge_case_double_digit_prime():
    assert prime_fib(2) == 3

def test_edge_case_single_digit_fibonacci():
    assert prime_fib(4) == 13

def test_edge_case_double_digit_fibonacci():
    assert prime_fib(5) == 89
