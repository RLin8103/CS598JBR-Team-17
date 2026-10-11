import pytest
from HumanEval_148 import *

def test_example():
    assert bf('Jupiter', 'Neptune') == ('Saturn', 'Uranus'), 'First test error: ' + str(len(bf('Jupiter', 'Neptune')))

def test_same_planets():
    assert bf('Jupiter', 'Jupiter') == (), 'Second test error: ' + str(bf('Jupiter', 'Jupiter'))

def test_planet1_not_exist():
    assert bf('Pluto', 'Neptune') == (), 'Third test error: ' + str(bf('Pluto', 'Neptune'))

def test_planet2_not_exist():
    assert bf('Jupiter', 'Pluto') == (), 'Fourth test error: ' + str(bf('Jupiter', 'Pluto'))

def test_planet1_closer_to_sun():
    assert bf('Mercury', 'Earth') == ('Venus',), 'Fifth test error: ' + str(bf('Mercury', 'Earth'))

def test_planet2_closer_to_sun():
    assert bf('Earth', 'Mercury') == ('Venus',), 'Sixth test error: ' + str(bf('Earth', 'Mercury'))

def test_both_planets_closer_to_sun():
    assert bf('Mercury', 'Mars') == ('Venus', 'Earth'), 'Seventh test error: ' + str(bf('Mercury', 'Mars'))

def test_planet1_is_planet2():
    assert bf('Jupiter', 'Jupiter') == (), 'Eighth test error: ' + str(bf('Jupiter', 'Jupiter'))

def test_planet1_is_closer_to_sun():
    assert bf('Mercury', 'Jupiter') == ('Venus', 'Earth', 'Mars', 'Saturn', 'Uranus'), 'Ninth test error: ' + str(bf('Mercury', 'Jupiter'))

def test_planet2_is_closer_to_sun():
    assert bf('Jupiter', 'Mercury') == ('Saturn', 'Uranus', 'Neptune'), 'Tenth test error: ' + str(bf('Jupiter', 'Mercury'))

def test_both_planets_are_closer_to_sun():
    assert bf('Mercury', 'Neptune') == ('Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus'), 'Eleventh test error: ' + str(bf('Mercury', 'Neptune'))

def test_planet1_is_furthest_from_sun():
    assert bf('Neptune', 'Mercury') == ('Jupiter', 'Saturn', 'Uranus'), 'Twelfth test error: ' + str(bf('Neptune', 'Mercury'))

def test_planet2_is_furthest_from_sun():
    assert bf('Mercury', 'Pluto') == (), 'Thirteenth test error: ' + str(bf('Mercury', 'Pluto'))

def test_both_planets_are_furthest_from_sun():
    assert bf('Neptune', 'Pluto') == (), 'Fourteenth test error: ' + str(bf('Neptune', 'Pluto'))

def test_planet2_is_closer_to_closer_to_sun():
    assert bf('Jupiter', 'Mercury') == ('Saturn', 'Uranus', 'Neptune'), 'Tenth test error: ' + str(bf('Jupiter', 'Mercury'))
