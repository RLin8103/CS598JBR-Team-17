import pytest
from HumanEval_18 import *

def test_empty_string():
    assert how_many_times('', 'a') == 0

def test_substring_not_in_string():
    assert how_many_times('abc', 'd') == 0

def test_substring_in_string():
    assert how_many_times('abcabc', 'abc') == 2

def test_single_character_substring():
    assert how_many_times('aaaaa', 'a') == 5

def test_overlapping_substrings():
    assert how_many_times('ababa', 'aba') == 2

def test_substring_at_start():
    assert how_many_times('aaabaa', 'aa') == 2

def test_substring_at_end():
    assert how_many_times('ababa', 'bab') == 1

def test_substring_at_start_and_end():
    assert how_many_times('bababa', 'bab') == 2

def test_substring_same_as_string():
    assert how_many_times('abc', 'abc') == 1

def test_substring_greater_than_string():
    assert how_many_times('abc', 'abcd') == 0

def test_string_greater_than_substring():
    assert how_many_times('abcabc', 'abcde') == 0

def test_empty_substring():
    assert how_many_times('abcabc', '') == 0

def test_empty_string_and_empty_substring():
    assert how_many_times('', '') == 0
