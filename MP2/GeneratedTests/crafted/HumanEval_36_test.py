import pytest
from HumanEval_36 import *

def test_fizz_buzz_0():
    assert fizz_buzz(0) == 0

def test_fizz_buzz_1():
    assert fizz_buzz(1) == 0

def test_fizz_buzz_11():
    assert fizz_buzz(11) == 1

def test_fizz_buzz_13():
    assert fizz_buzz(13) == 1

def test_fizz_buzz_14():
    assert fizz_buzz(14) == 1

def test_fizz_buzz_22():
    assert fizz_buzz(22) == 0

def test_fizz_buzz_33():
    assert fizz_buzz(33) == 1

def test_fizz_buzz_44():
    assert fizz_buzz(44) == 0

def test_fizz_buzz_55():
    assert fizz_buzz(55) == 1

def test_fizz_buzz_66():
    assert fizz_buzz(66) == 0

def test_fizz_buzz_77():
    assert fizz_buzz(77) == 1

def test_fizz_buzz_88():
    assert fizz_buzz(88) == 0

def test_fizz_buzz_99():
    assert fizz_buzz(99) == 1

def test_fizz_buzz_100():
    assert fizz_buzz(100) == 0
