import pytest
from HumanEval_1 import *

def test_example():
    assert separate_paren_groups('(()()) ((())) () ((())()())') == ['(()())', '((()))', '', '((())()())']

def test_empty_string():
    assert separate_paren_groups('') == ['']

def test_single_group():
    assert separate_paren_groups('(())') == ['(())']

def test_single_parenthesis():
    assert separate_paren_groups('()') == ['()']

def test_multiple_groups():
    assert separate_paren_groups('((())) () (())') == ['((()))', '', '(())']

def test_nested_groups():
    assert separate_paren_groups('(((()))) () (((())))') == ['(((())))', '', '(((())))']

def test_no_spaces():
    assert separate_paren_groups('(()(()))()()((()))') == ['(()(()))()()((()))']

def test_spaces_in_between():
    assert separate_paren_groups('( ) (( )) (( )( ))') == ['()', '(())', '(()())']

def test_spaces_at_start_and_end():
    assert separate_paren_groups(' ( () ) ( ( ) ) ') == ['()', '()']

def test_spaces_in_between_and_at_start_and_end():
    assert separate_paren_groups(' ( () ) ( ( ) ) ') == ['()', '()']

def test_no_parenthesis():
    assert separate_paren_groups('no parenthesis here') == ['no parenthesis here']

def test_no_balanced_parenthesis():
    assert separate_paren_groups('(((())))))(((()') == ['(((()))))', '((()']

def test_negative_numbers():
    assert separate_paren_groups('(-1) (2) (-3)') == ['(-1)', '(2)', '(-3)']

def test_zero():
    assert separate_paren_groups('0 (1) 0 (2)') == ['0', '(1)', '0', '(2)']
