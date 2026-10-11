import pytest
from HumanEval_127 import *

def test_example():
    assert intersection((1, 2), (2, 3)) == 'NO'

def test_intersection_same_interval():
    assert intersection((1, 3), (1, 3)) == 'NO'

def test_intersection_start_same():
    assert intersection((1, 3), (1, 4)) == 'YES'

def test_intersection_end_same():
    assert intersection((1, 3), (2, 3)) == 'NO'

def test_intersection_one_point():
    assert intersection((1, 1), (1, 2)) == 'NO'

def test_intersection_one_point_same():
    assert intersection((1, 1), (1, 1)) == 'NO'

def test_intersection_one_point_in_interval():
    assert intersection((1, 2), (1, 2)) == 'NO'

def test_intersection_one_point_in_interval_same():
    assert intersection((1, 2), (1, 1)) == 'NO'

def test_intersection_one_point_in_interval_end():
    assert intersection((1, 2), (2, 2)) == 'NO'

def test_intersection_one_point_in_interval_start():
    assert intersection((1, 2), (1, 1)) == 'NO'

def test_intersection_one_point_in_interval_start_same():
    assert intersection((1, 2), (1, 3)) == 'YES'

def test_intersection_one_point_in_interval_end_same():
    assert intersection((1, 2), (0, 2)) == 'YES'

def test_intersection_one_point_in_interval_start_end_same():
    assert intersection((1, 2), (1, 2)) == 'NO'

def test_intersection_one_point_in_interval_start_end_same_prime():
    assert intersection((1, 2), (1, 1)) == 'NO'

def test_intersection_one_point_in_interval_start_end_same_prime_2():
    assert intersection((1, 2), (2, 2)) == 'NO'

def test_intersection_one_point_in_interval_start_end_same_prime_3():
    assert intersection((1, 2), (0, 1)) == 'NO'

def test_intersection_one_point_in_interval_start_end_same_prime_4():
    assert intersection((1, 2), (2, 1)) == 'NO'

def test_intersection_one_point_in_interval_start_end_same_prime_5():
    assert intersection((1, 2), (0, 0)) == 'NO'

def test_intersection_one_point_in_interval_start_end_same_prime_6():
    assert intersection((1, 2), (3, 3)) == 'NO'

def test_intersection_one_point_in_interval_start_end_same_prime_7():
    assert intersection((1, 2), (4, 4)) == 'NO'

def test_intersection_one_point_in_interval_start_end_same_prime_8():
    assert intersection((1, 2), (3, 4)) == 'YES'

def test_intersection_one_point_in_interval_start_end_same_prime_9():
    assert intersection((1, 2), (0, 3)) == 'YES'

def test_intersection_one_point_in_interval_start_end_same_prime_10():
    assert intersection((1, 2), (-1, 1)) == 'YES'

def test_intersection_one_point_in_interval_start_end_same_prime_11():
    assert intersection((1, 2), (-2, 2)) == 'YES'

def test_intersection_one_point_in_interval_start_end_same_prime_12():
    assert intersection((1, 2), (-3, 1)) == 'YES'

def test_intersection_one_point_in_interval_start_end_same_prime_13():
    assert intersection((1, 2), (-4, 0)) == 'YES'

def test_intersection_one_point_in_interval_start_end_same_prime_14():
    assert intersection((1, 2), (-3, 0)) == 'YES'

def test_intersection_one_point_in_interval_start_end_same_prime_15():
    assert intersection((1, 2), (-4, 2)) == 'YES'
