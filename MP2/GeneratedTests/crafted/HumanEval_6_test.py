import pytest
from HumanEval_6 import *

def test_example():
    assert parse_nested_parens('(()()) ((())) () ((())()())') == [2, 3, 1, 3]

def test_empty_string():
    assert parse_nested_parens('') == []

def test_single_group():
    assert parse_nested_parens('(()())') == [2]

def test_single_group_with_spaces():
    assert parse_nested_parens(' (()()) ') == [2]

def test_multiple_groups_with_spaces():
    assert parse_nested_parens(' (()()) ((())) () ((())()()) ') == [2, 3, 1, 3]

def test_no_nested_parens():
    assert parse_nested_parens('abcdefgh') == [0]

def test_nested_parens_at_start():
    assert parse_nested_parens('(((()))) abcdefgh') == [4]

def test_nested_parens_at_end():
    assert parse_nested_parens('abcdefgh (()())') == [2]

def test_nested_parens_in_middle():
    assert parse_nested_parens('abc (()()) def') == [2]

def test_nested_parens_with_text():
    assert parse_nested_parens('abc (()()) def (hello)') == [2, 1]

def test_nested_parens_with_zero():
    assert parse_nested_parens('abc (()()) def 0') == [2, 1]

def test_nested_parens_with_negative():
    assert parse_nested_parens('abc (()()) def -1') == [2, 1]

def test_nested_parens_with_boundary_values():
    assert parse_nested_parens('abc (()()) def 100') == [2, 1]
