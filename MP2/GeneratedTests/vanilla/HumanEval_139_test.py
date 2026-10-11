import pytest
from HumanEval_139 import *

def test_special_factorial_0():
    assert special_factorial(0) == 1

def test_special_factorial_1():
    assert special_factorial(1) == 1

def test_special_factorial_5():
    assert special_factorial(5) == 120

def test_special_factorial_10():
    assert special_factorial(10) == 3628800
