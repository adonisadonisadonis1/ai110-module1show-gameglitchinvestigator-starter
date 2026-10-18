import pytest

from logic_utils import check_guess, get_hint_message

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# Regression tests for Bug 1: hint messages were backwards.

def test_too_high_hint_says_go_lower():
    # Secret 5, guess 50 used to show "Go HIGHER!"
    message = get_hint_message(check_guess(50, 5))
    assert "LOWER" in message


def test_too_low_hint_says_go_higher():
    # Secret 5, guess 3 used to show "Go LOWER!"
    message = get_hint_message(check_guess(3, 5))
    assert "HIGHER" in message


# Regression tests for Bug 2: numbers were compared as strings.

def test_comparison_is_numeric_not_alphabetical():
    # As strings, "9" > "50" and "100" < "50"
    assert check_guess(9, 50) == "Too Low"
    assert check_guess(100, 50) == "Too High"


def test_string_secret_is_not_silently_compared_as_text():
    # The old fallback returned "Too High" here instead of raising
    with pytest.raises(TypeError):
        check_guess(9, "50")
