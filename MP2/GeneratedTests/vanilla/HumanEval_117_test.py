import pytest
from HumanEval_117 import *

def test_select_words():
    assert select_words('hello world', 2) == ['hello']
    assert select_words('beautiful day', 3) == ['beautiful']
    assert select_words('apple orange banana', 3) == ['banana']
    assert select_words('orange banana apple', 3) == ['banana']
    assert select_words('apple orange banana', 4) == []
    assert select_words('', 2) == []
