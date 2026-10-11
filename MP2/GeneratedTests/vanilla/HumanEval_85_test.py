import pytest
from HumanEval_85 import *

def test_add():
    assert add([1, 2, 3, 4, 5]) == 6
    assert add([2, 3, 4, 5, 6]) == 10
    assert add([1, 2, 3, 4, 5, 6]) == 12
    assert add([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 30
    assert add([2, 3, 4, 5, 6, 7, 8, 9, 10]) == 20
    assert add([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]) == 50
    assert add([1]) == 0
    assert add([]) == 0
