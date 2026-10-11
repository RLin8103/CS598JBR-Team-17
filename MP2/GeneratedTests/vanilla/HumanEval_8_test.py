import pytest
from HumanEval_8 import *

def test_sum_product():
    assert sum_product([1, 2, 3, 4, 5]) == (15, 120)
    assert sum_product([0, 0, 0, 0]) == (0, 0)
    assert sum_product([-1, 2, -3, 4]) == (-2, -24)
    assert sum_product([10, 20, 30, 40]) == (100, 24000)
