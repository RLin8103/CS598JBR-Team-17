import pytest
from HumanEval_117 import *

def test_example():
    assert select_words('Mary had a little lamb', 4) == ['little'], 'First test error: ' + str(select_words('Mary had a little lamb', 4))

def test_empty_string():
    assert select_words('', 3) == [], 'Second test error: ' + str(select_words('', 3))

def test_single_word():
    assert select_words('hello', 2) == [], 'Third test error: ' + str(select_words('hello', 2))

def test_zero_consonants():
    assert select_words('hello', 0) == ['hello'], 'Fourth test error: ' + str(select_words('hello', 0))

def test_negative_consonants():
    assert select_words('hello', -1) == [], 'Fifth test error: ' + str(select_words('hello', -1))

def test_multiple_words_same_consonants():
    assert select_words('hello world', 2) == ['world'], 'Sixth test error: ' + str(select_words('hello world', 2))

def test_multiple_words_different_consonants():
    assert select_words('hello world', 3) == ['hello'], 'Seventh test error: ' + str(select_words('hello world', 3))

def test_uppercase_letters():
    assert select_words('Mary', 1) == ['Mary'], 'Eighth test error: ' + str(select_words('Mary', 1))

def test_vowels_only():
    assert select_words('aeiou', 0) == ['aeiou'], 'Ninth test error: ' + str(select_words('aeiou', 0))

def test_consonants_only():
    assert select_words('bcd', 3) == ['bcd'], 'Tenth test error: ' + str(select_words('bcd', 3))

def test_boundary_values():
    assert select_words('Mary had a little lamb', 13) == [], 'Eleventh test error: ' + str(select_words('Mary had a little lamb', 13))

def test_boundary_values_2():
    assert select_words('Mary had a little lamb', 0) == ['Mary', 'a', 'little', 'lamb'], 'Twelfth test error: ' + str(select_words('Mary had a little lamb', 0))

def test_boundary_values_3():
    assert select_words('Mary had a little lamb', 1) == ['had', 'a', 'lamb'], 'Thirteenth test error: ' + str(select_words('Mary had a little lamb', 1))
