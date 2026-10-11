import pytest
from HumanEval_127 import *

def test_intersection_no_intersection():
    assert intersection([1, 2], [3, 4]) == 'NO'

def test_intersection_intersect_at_end():
    assert intersection([1, 3], [2, 4]) == 'YES'

def test_intersection_intersect_at_start():
    assert intersection([2, 4], [1, 3]) == 'YES'

def test_intersection_intersect_in_middle():
    assert intersection([1, 4], [2, 3]) == 'YES'

def test_intersection_same_interval():
    assert intersection([1, 3], [1, 3]) == 'YES'

def test_intersection_one_point_interval():
    assert intersection([2, 2], [1, 3]) == 'YES'

def test_intersection_no_intersection_one_point_interval():
    assert intersection([1, 1], [2, 3]) == 'NO'

def test_intersection_empty_interval():
    assert intersection([1, 1], [3, 3]) == 'NO'
