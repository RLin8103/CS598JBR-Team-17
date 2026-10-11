import pytest
from HumanEval_36 import *

def test_fizz_buzz():
    assert fizz_buzz(0) == 0
    assert fizz_buzz(1) == 0
    assert fizz_buzz(11) == 1
    assert fizz_buzz(13) == 1
    assert fizz_buzz(14) == 0
    assert fizz_buzz(100) == 1
    assert fizz_buzz(1000) == 1
    assert fizz_buzz(10000) == 1
