# NOTES

Verified facts:
- Task folder initially contained only README.md.
- f = `python "avo-lab\checkers\m1_checker.py" "avo-lab\evals\runs\treat-m1"` run from repo root (per task instructions; README shows an older tasks/ path but the runs path is authoritative).
- PASS requires 100/100; checker groups: imports, has-is-balanced, basic-balance, nesting-interleaving, quotes-swallow, escapes, unterminated-tails (5 case groups + 2 import checks).
- Checker imports solution.py from the given folder and looks up callable is_balanced(s).
- Winning design: single pass, three states — `escaped` flag (backslash consumes next char in ALL contexts, incl. inside quotes), `quote` var (None / `'` / `"`; opposite quote chars are inert inside a quote), bracket `stack` with close→open dict for mismatch detection. Return `len(stack) == 0`; unterminated tail contributes nothing and is not False by itself.
- README worked-example table: the displayed literal for example 6 (`'"\\("'`) decodes to chars `"`,`\`,`(` → True, contradicting its own chars column (`\`,`"`,`(` → False). Trust the chars/why columns; hidden battery follows the why-column semantics.

UNVERIFIED guesses:
- None remaining. All 7 worked examples plus 12 extra edge cases verified via sanity.py (19 OK) and full battery green.
