import pytest
from HumanEval_4 import *

def test_mean_absolute_deviation():
    assert mean_absolute_deviation([1.0, 2.0, 3.0, 4.0, 5.0]) == 1.8
    assert mean_absolute_deviation([0.0, 1.0, 2.0]) == 1.0
    assert mean_absolute_deviation([-1.0, -2.0, -3.0]) == 2.0
    assert mean_absolute_deviation([1.0]) == 0.0
    assert mean_absolute_deviation([0.0, 0.0, 0.0]) == 0.0
    assert mean_absolute_deviation([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]) == 1.8333333333333333
