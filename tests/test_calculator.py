import pytest

from app.agents.tools import calculate


def test_calculate_valid_expression():
    assert calculate("(120 - 100) / 100 * 100") == 20


def test_calculate_rejects_function_call():
    with pytest.raises(ValueError):
        calculate("__import__('os').system('dir')")
