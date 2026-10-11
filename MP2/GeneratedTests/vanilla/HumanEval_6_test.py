import pytest
from HumanEval_6 import *

def test_parse_nested_parens():
    assert parse_nested_parens('()') == [1]
    assert parse_nested_parens('(())') == [2]
    assert parse_nested_parens('()()') == [1, 1]
    assert parse_nested_parens('((()))') == [3]
    assert parse_nested_parens('((()))()') == [3, 1]
    assert parse_nested_parens('') == []
    assert parse_nested_parens(' ') == []
    assert parse_nested_parens('  ()  ') == [1]
    assert parse_nested_parens('  (())  ') == [2]
