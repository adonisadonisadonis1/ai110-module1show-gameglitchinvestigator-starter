# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] Describe the game's purpose.
- [x] Detail which bugs you found.
- [x] Explain what fixes you applied.

**Game purpose.** Glitchy Guesser is a Streamlit number-guessing game. The app picks a secret number in a range set by the difficulty (Normal is 1 to 100 with 8 attempts). After each guess it tells you to go higher or lower until you find the number or run out of attempts. The starter code was written by an AI and shipped with bugs that made the hints unreliable.

**Bugs found.** I ran the app, played several games with the Developer Debug Info panel open, and reproduced three bugs (full log in `reflection.md`):
1. **Backwards hints.** In `check_guess`, a guess that was too high said "📈 Go HIGHER!", and one that was too low said "📉 Go LOWER!". With secret 5, guessing 3 said "Go LOWER!".
2. **Secret compared as a string.** On every even-numbered attempt, `app.py` turned the secret into a `str`. `check_guess` then hit a `TypeError` comparing an int with a str, caught it silently, and compared the values as text, so `"9" > "50"` and `"100" < "50"`. The hints flip-flopped from one attempt to the next.
3. **New Game doesn't reset the game.** After a win, clicking "New Game 🔁" kept showing "You already won", because `status` was never reset. *(Not fixed yet.)*

**Fixes applied (bugs 1 and 2).**
- Moved `get_range_for_difficulty`, `parse_guess`, `check_guess`, and `update_score` from `app.py` into `logic_utils.py`, and imported them in `app.py`.
- `check_guess` now returns only the outcome (`"Win"`, `"Too High"`, `"Too Low"`), as the original tests expect. The new `get_hint_message(outcome)` returns the correctly paired hint: Too High → "📉 Go LOWER!", Too Low → "📈 Go HIGHER!".
- `app.py` now always passes the int secret, and the silent `except TypeError` string-comparison fallback was removed.
- Added 4 regression tests in `tests/test_game_logic.py`. Three of them failed against the original code and all pass now.

**Known issues still present:** New Game not resetting (bug 3); attempts starting at 1 (one fewer guess than allowed); the secret not being re-rolled when difficulty changes; the hard-coded "between 1 and 100" message; Hard having a smaller range than Normal; and odd scoring in `update_score` (see the walkthrough below).

## 📸 Demo Walkthrough

Below is a real game played on the fixed app (`python -m streamlit run app.py`), on **Normal** difficulty with the Developer Debug Info panel open. The secret for this game was **11**. The guesses follow the hints only, cutting the remaining range roughly in half each time. The score is the value the debug panel showed after each guess.

1. **Start the app.** The sidebar shows "Range: 1 to 100" and "Attempts allowed: 8". The info box says "Guess a number between 1 and 100. Attempts left: 7". Score: 0.
2. **Guess 50** → "📉 Go LOWER!" (50 > 11, correct). Score: **5**.
3. **Guess 25** → "📉 Go LOWER!" Score: **0**.
4. **Guess 12** → "📉 Go LOWER!" Score: **5**.
5. **Guess 6** → "📈 Go HIGHER!" (6 < 11, correct). Score: **0**.
6. **Guess 9** → "📈 Go HIGHER!" Score: **−5**.
7. **Guess 10** → "📈 Go HIGHER!" Score: **−10**. The info box now says "Attempts left: 1".
8. **Guess 11** → "🎉 Correct!", balloons, and "**You won! The secret was 11. Final score: 0**".

Every hint pointed the right way on both odd and even attempts. Before the fix, guess 50 would have said "Go HIGHER!" and guess 6 "Go LOWER!".

*Notes on the score:* the score swings up and down because `update_score` (which I have not fixed) gives +5 for a "Too High" guess on an even attempt number and −5 otherwise. The win added 10 points (the minimum, since it came on the 8th value of the attempt counter), for a final score of 0. The Developer Debug Info panel updates one step late, because it is drawn before the new guess is processed.

## 🧪 Test Results

Output of `python -m pytest -v` on the fixed code (3 original tests plus 4 regression tests for bugs 1 and 2). Lines showing local folder paths were removed:

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
collecting ... collected 7 items

tests/test_game_logic.py::test_winning_guess PASSED                      [ 14%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 28%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 42%]
tests/test_game_logic.py::test_too_high_hint_says_go_lower PASSED        [ 57%]
tests/test_game_logic.py::test_too_low_hint_says_go_higher PASSED        [ 71%]
tests/test_game_logic.py::test_comparison_is_numeric_not_alphabetical PASSED [ 85%]
tests/test_game_logic.py::test_string_secret_is_not_silently_compared_as_text PASSED [100%]

============================== 7 passed in 0.01s ===============================
```

Challenge 1 (Advanced Edge-Case Testing) was not attempted. These are core regression tests only.

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]

No stretch features were attempted.
