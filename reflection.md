# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

The first time I ran `python -m streamlit run app.py`, the app started without any errors (the terminal only showed an unrelated urllib3/LibreSSL warning) and displayed a title, a "Make a guess" box, a Developer Debug Info expander, a text input, and Submit / New Game buttons. It looked normal at first, but before I had guessed anything it already said "Attempts left: 7" even though the sidebar said 8 attempts were allowed. Once I started guessing, the hints pointed me in the wrong direction: with a secret of 5, guessing 50 told me "Go HIGHER!" and guessing 3 told me "Go LOWER!". The hints were also inconsistent between guesses, because on every other attempt the game compares numbers as text. After I won, clicking "New Game" did not let me play again; the game stayed stuck on "You already won. Start a new game to play again."

**Bug 1: The hints are backwards**
- **Input / trigger:** Any wrong guess when the attempt counter is odd (so the secret is still an int). Example: secret = 5, guess `3` (Normal difficulty).
- **Expected:** Guessing 3 when the secret is 5 should say "Go HIGHER!"
- **Actual:** The game said "📉 Go LOWER!" (and guessing 50 vs. 5 said "📈 Go HIGHER!").
- **Console output:** No error. Calling `check_guess(60, 50)` directly returns `('Too High', '📈 Go HIGHER!')`.
- **Suspected location:** `check_guess()` in `app.py` (lines 37–40, and again in the fallback at lines 45–47).
- **Explanation:** The outcome labels are right but the messages attached to them are swapped. When the guess is too high, the player needs to go *lower*, but the code returns "Go HIGHER!".

**Bug 2: On every even attempt the secret is compared as a string**
- **Input / trigger:** Any guess on an even-numbered attempt (attempt counter 2, 4, 6...). Example: secret = 50, guess `9` or `100`.
- **Expected:** Numbers are compared numerically: 9 < 50 ("Too Low") and 100 > 50 ("Too High").
- **Actual:** `check_guess(9, "50")` returns "Too High" and `check_guess(100, "50")` returns "Too Low". In the game (secret 5), guessing 40 said "Go LOWER!" while guessing 50 two attempts earlier said "Go HIGHER!". Both guesses were above the secret but got opposite hints, so the hints flip-flop depending on the attempt number.
- **Console output:** No visible error. Inside `check_guess`, `int > str` raises a `TypeError`, which is caught silently, and the code falls back to comparing `str(guess)` against the string secret.
- **Suspected location:** `app.py` lines 158–161 (`if st.session_state.attempts % 2 == 0: secret = str(st.session_state.secret)`) together with the `except TypeError` block in `check_guess()` (lines 41–47).
- **Explanation:** Strings are compared character by character (alphabetical order), not by value. `"9" > "50"` is True because `'9' > '5'`, and `"100" < "50"` because `'1' < '5'`.

**Bug 3: "New Game" does not actually start a new game**
- **Input / trigger:** Win (or lose) a game, then click "New Game 🔁".
- **Expected:** Status, attempts, score, and history reset, a new secret is picked in the selected difficulty's range, and I can guess again.
- **Actual:** The debug panel showed a new secret (19) and Attempts: 0, but the page still said "You already won. Start a new game to play again." Submitting a new guess (20) did nothing. Score (35) and History ([50, 3, 40, 5]) were carried over from the old game.
- **Console output:** No error. The game blocks at `st.stop()`.
- **Suspected location:** The `if new_game:` block in `app.py` (lines 134–138), plus the status check at lines 140–145.
- **Explanation:** The New Game handler only resets `attempts` and `secret`. It never sets `st.session_state.status` back to `"playing"`, so the status check at line 140 stops the script before any guess is processed. It also ignores difficulty (`random.randint(1, 100)`) and sets attempts to 0 while a fresh session starts at 1.

**Other things I noticed (not in the main three):**
- `attempts` starts at 1 (line 96), so the game shows one fewer attempt than allowed and ends early. On Easy (6 allowed) I was told "Out of attempts!" after only 5 guesses, while the info box still said "Attempts left: 1".
- The secret is created only once, using the difficulty at first load. After I switched to Easy (range 1 to 20), the secret was still 99, which made the game impossible to win.
- The info text is hardcoded to "Guess a number between 1 and 100" for every difficulty, and "Hard" uses a smaller range (1 to 50) than "Normal" (1 to 100).
- `pytest` currently fails 3/3 tests with `NotImplementedError` because the functions in `logic_utils.py` are still stubs.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error | Suspected Code Location |
|-------|-------------------|-----------------|------------------------|-------------------------|
| Normal, secret = 5, guess `3` (odd attempt) | Hint says "Go HIGHER!" | Hint says "📉 Go LOWER!" (guess 50 also said "Go HIGHER!") | No error; `check_guess(60, 50)` returns `('Too High', '📈 Go HIGHER!')` | `check_guess()` in `app.py`, lines 37–40 (messages swapped) |
| Secret = 50, guess `9` or `100` on an even attempt | 9 → Too Low; 100 → Too High (numeric comparison) | 9 → "Too High"; 100 → "Too Low"; in-game hints flip-flop between attempts | No visible error; `TypeError` (int vs str) is caught silently and the strings are compared instead | `app.py` lines 158–161 (`secret = str(...)` on even attempts) + `except TypeError` in `check_guess()`, lines 41–47 |
| Win a game, then click "New Game 🔁" and submit guess `20` | Game resets (status, score, history) and accepts new guesses | Still shows "You already won. Start a new game to play again."; guess ignored; old score/history kept | No error; script halts at `st.stop()` | `if new_game:` block, `app.py` lines 134–138 (does not reset `status`) and lines 140–145 |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
