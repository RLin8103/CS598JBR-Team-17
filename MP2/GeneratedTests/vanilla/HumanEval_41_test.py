import pytest
from HumanEval_41 import *

def test_car_race_collision_positive():
    assert car_race_collision(5) == 25
    assert car_race_collision(10) == 100

def test_car_race_collision_negative():
    assert car_race_collision(-5) == 25
    assert car_race_collision(-10) == 100

def test_car_race_collision_zero():
    assert car_race_collision(0) == 0
