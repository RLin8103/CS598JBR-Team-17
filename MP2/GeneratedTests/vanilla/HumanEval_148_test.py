import pytest
from HumanEval_148 import *

def test_bf_valid_input():
    assert bf('Earth', 'Mars') == ('Mercury', 'Venus')
    assert bf('Mars', 'Earth') == ('Mercury', 'Venus')
    assert bf('Earth', 'Jupiter') == ('Mercury', 'Venus', 'Saturn', 'Uranus')
    assert bf('Jupiter', 'Earth') == ('Mercury', 'Venus', 'Saturn', 'Uranus')

def test_bf_same_planet():
    assert bf('Earth', 'Earth') == ()

def test_bf_invalid_planet():
    assert bf('Earth', 'Pluto') == ()
    assert bf('Pluto', 'Earth') == ()
