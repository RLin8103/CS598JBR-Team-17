import pytest
from HumanEval_55 import *

def test_fib_zero():
    assert fib(0) == 0

def test_fib_one():
    assert fib(1) == 1

def test_fib_two():
    assert fib(2) == 1

def test_fib_three():
    assert fib(3) == 2

def test_fib_four():
    assert fib(4) == 3

def test_fib_five():
    assert fib(5) == 5

def test_fib_six():
    assert fib(6) == 8

def test_fib_seven():
    assert fib(7) == 13

def test_fib_eight():
    assert fib(8) == 21

def test_fib_nine():
    assert fib(9) == 34

def test_fib_ten():
    assert fib(10) == 55

def test_fib_negative():
    with pytest.raises(RecursionError):
        fib(-1)

def test_fib_large():
    assert fib(50) == 12586269025

def test_fib_large_negative():
    with pytest.raises(RecursionError):
        fib(-50)
