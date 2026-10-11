import pytest
from HumanEval_105 import *

def test_by_length():
    assert by_length([1, 2, 3, 4, 5]) == ['One', 'Two', 'Three', 'Four', 'Five']
    assert by_length([6, 7, 8, 9]) == ['Six', 'Seven', 'Eight', 'Nine']
    assert by_length([1, 2, 3, 4, 5, 6, 7, 8, 9]) == ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    assert by_length([2, 3, 1]) == ['Two', 'Three', 'One']
    assert by_length([4, 5, 6, 7, 8, 9]) == ['Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    assert by_length([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    assert by_length([]) == []
