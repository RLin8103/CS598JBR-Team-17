import pytest
from HumanEval_115 import *

def test_example():
    assert max_fill([[0, 0, 1, 0], [0, 1, 0, 0], [1, 1, 1, 1]], 1) == 6, 'Error'

def test_empty_grid():
    assert max_fill([], 1) == 0, 'Error'

def test_single_well():
    assert max_fill([[1, 1, 1, 1]], 2) == 2, 'Error'

def test_all_zeros():
    assert max_fill([[0, 0, 0, 0], [0, 0, 0, 0]], 1) == 0, 'Error'

def test_capacity_one():
    assert max_fill([[1, 1, 1, 1], [1, 1, 1, 1]], 1) == 8, 'Error'

def test_capacity_two():
    assert max_fill([[2, 2, 2, 2], [2, 2, 2, 2]], 2) == 4, 'Error'

def test_capacity_three():
    assert max_fill([[3, 3, 3, 3], [3, 3, 3, 3]], 3) == 3, 'Error'

def test_capacity_four():
    assert max_fill([[4, 4, 4, 4], [4, 4, 4, 4]], 4) == 2, 'Error'

def test_capacity_five():
    assert max_fill([[5, 5, 5, 5], [5, 5, 5, 5]], 5) == 2, 'Error'

def test_capacity_six():
    assert max_fill([[6, 6, 6, 6], [6, 6, 6, 6]], 6) == 2, 'Error'

def test_capacity_seven():
    assert max_fill([[7, 7, 7, 7], [7, 7, 7, 7]], 7) == 2, 'Error'

def test_capacity_eight():
    assert max_fill([[8, 8, 8, 8], [8, 8, 8, 8]], 8) == 2, 'Error'

def test_capacity_nine():
    assert max_fill([[9, 9, 9, 9], [9, 9, 9, 9]], 9) == 2, 'Error'

def test_capacity_ten():
    assert max_fill([[10, 10, 10, 10], [10, 10, 10, 10]], 10) == 2, 'Error'
