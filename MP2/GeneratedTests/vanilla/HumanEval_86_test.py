import pytest
from HumanEval_86 import *

def test_anti_shuffle():
    assert anti_shuffle('ab cd') == 'ab cd'
    assert anti_shuffle('hello world') == 'dlrow olleh'
    assert anti_shuffle('') == ''
    assert anti_shuffle('a') == 'a'
    assert anti_shuffle('of') == 'of'
