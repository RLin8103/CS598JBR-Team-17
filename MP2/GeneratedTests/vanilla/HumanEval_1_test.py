import pytest
from HumanEval_1 import *

def test_separate_paren_groups():
    assert separate_paren_groups('()') == ['()']
    assert separate_paren_groups('((()))()(())') == ['((()))', '()', '(())']
    assert separate_paren_groups('') == []
    assert separate_paren_groups('(()()()())') == ['(()()()())']
    assert separate_paren_groups(')(') == [')(']
    assert separate_paren_groups('((())())(()(()))') == ['((())())', '(()(()))']
