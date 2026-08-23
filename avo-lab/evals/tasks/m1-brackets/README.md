# M1 — Quoted-bracket validator (medium)

## Task
Create `solution.py` in this folder defining:

```python
def is_balanced(s: str) -> bool:
```

Python 3 standard library only. The function decides whether the bracket
characters in `s` are balanced, where brackets inside quoted sections are
ignored.

## Precise rules

1. Bracket characters are `(` `)` `[` `]` `{` `}`.
2. Outside quotes they must form properly matched, properly nested pairs.
   Any other character is neutral.
3. A backslash `\` escapes the immediately following character in ALL contexts.
   An escaped character has no special meaning (an escaped quote does not open
   or close a string; an escaped bracket is neutral).
4. An unescaped `'` toggles single-quoted state until the next unescaped `'`.
   Same for `"` with double quotes. Inside a quoted section every character is
   ignored — including brackets and the opposite quote character.
5. If input ends while inside a quoted section, everything from the opening
   quote to EOF is ignored (the unterminated tail contributes no brackets).
   Unterminated quotes do not by themselves make the result False.

## Worked examples

| input (python literal) | chars | result | why |
|---|---|---|---|
| `"()[]"` | `(` `)` `[` `]` | True | plain balance |
| `"([)]"` | | False | interleaved, improper nesting |
| `"{[()]}"` | | True | deep nesting |
| `"'('"` | `'` `(` | True | bracket swallowed by unterminated string |
| `"'(x)'("` | `'` `(` x `)` `'` `(` | False | trailing `(` sits outside any string |
| `'"\\("'` | `\` `"` `(` | False | `\` escapes the `"` → no string ever opens; `(` unpaired |
| `"'\\'('"` | `'` `\` `'` `(` | True | `\'` is escaped → still inside string; `(` swallowed; tail ignored |

Write your own quick sanity script against these before running f.

## Verification (f)
From the repo root (hidden battery of 28 cases in 5 groups):

```
python "avo-lab/checkers/m1_checker.py" "avo-lab/evals/tasks/m1-brackets"
```

PASS requires 100/100. Do not read or modify anything under `avo-lab/checkers/`.
