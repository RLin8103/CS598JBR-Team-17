import pytest
from HumanEval_160 import *

def test_do_algebra_addition():
    operator = ['+', '+']
    operand = [1, 2, 3]
    assert do_algebra(operator, operand) == 6

def test_do_algebra_subtraction():
    operator = ['-']
    operand = [5, 2]
    assert do_algebra(operator, operand) == 3

def test_do_algebra_multiplication():
    operator = ['*', '*']
    operand = [1, 2, 3]
    assert do_algebra(operator, operand) == 6

def test_do_algebra_division():
    operator = ['/']
    operand = [10, 2]
    assert do_algebra(operator, operand) == 5

def test_do_algebra_exponentiation():
    operator = ['**']
    operand = [2, 3]
    assert do_algebra(operator, operand) == 8
