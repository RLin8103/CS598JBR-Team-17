import pytest
from HumanEval_86 import *

def test_example():
    assert anti_shuffle('Hi') == 'Hi'

def test_empty_string():
    assert anti_shuffle('') == ''

def test_single_word():
    assert anti_shuffle('hello') == 'ehllo'

def test_single_character():
    assert anti_shuffle('H') == 'H'

def test_zero():
    assert anti_shuffle('0') == '0'

def test_negative_numbers():
    assert anti_shuffle('-1') == '-1'

def test_multiple_words():
    assert anti_shuffle('Hello World!!!') == 'Hello !!!Wdlor'

def test_upper_case():
    assert anti_shuffle('ABC') == 'ABC'

def test_lower_case():
    assert anti_shuffle('abc') == 'abc'

def test_mixed_case():
    assert anti_shuffle('AbC') == 'AbC'

def test_special_characters():
    assert anti_shuffle('!@#$%^&*()') == '!@#$%^&*()'

def test_numbers_and_letters():
    assert anti_shuffle('123abc') == '123abc'

def test_numbers_and_special_characters():
    assert anti_shuffle('123!@#') == '123!@#'

def test_letters_and_special_characters():
    assert anti_shuffle('abc!@#') == 'abc!@#'

def test_all_cases():
    assert anti_shuffle('Hello World!!! 123#$%') == 'Hello !!!Wdlor 123#$%'
