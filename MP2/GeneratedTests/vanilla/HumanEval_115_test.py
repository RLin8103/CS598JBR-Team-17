import pytest
from HumanEval_115 import *

def test_max_fill():
    assert max_fill([[0, 0, 1, 0], [0, 1, 0, 0], [1, 1, 1, 1]], 1) == 6
    assert max_fill([[0, 0, 1, 1], [0, 0, 0, 0], [1, 1, 1, 1], [0, 1, 1, 1]], 2) == 5
    assert max_fill([[0, 0, 0], [0, 0, 0]], 5) == 0
    assert max_fill([[0, 0, 1, 0, 1], [0, 1, 0, 0, 1], [1, 1, 1, 1, 1]], 2) == 5
    assert max_fill([[0, 0, 1, 1, 1], [0, 0, 0, 0, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 1]], 3) == 4
    assert max_fill([[0, 0, 0], [0, 0, 0]], 1) == 0
