def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome.

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIX: Bug 2 - removed the `except TypeError` fallback that compared
    # str(guess) to a str secret ("9" > "50" is True). Both values are ints
    # now, so a type mix-up raises instead of giving a wrong hint. Suggested by
    # a separate AI debugging session; accepted after reproducing the bug.
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def get_hint_message(outcome: str):
    """Return the hint text shown to the player for an outcome."""
    # FIX: Bug 1 - the original messages were swapped. A guess that is too
    # high must tell the player to go LOWER, and vice versa. AI spotted the
    # swap; the message was split out of check_guess so the existing tests
    # (which expect check_guess to return only the outcome) stay unchanged.
    if outcome == "Win":
        return "🎉 Correct!"
    if outcome == "Too High":
        return "📉 Go LOWER!"
    return "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
