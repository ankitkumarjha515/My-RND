# X5 — Composed grid transformation (hard)

## Task
`examples.txt` shows four worked transformations. TWO rules are composed,
and their ORDER of application matters. Infer both rules AND the order from
the examples only, then transform the three unseen grids in `inputs/`.

Write outputs to:

```
outputs/h1_out.txt
outputs/h2_out.txt
outputs/h3_out.txt
```

Same format as inputs: rows on lines, integer cells separated by single
spaces, dimensions preserved.

## Rules of the game

- GENERALIZE. Hardcoding coordinates or example answers scores zero.
- One example is a negative case: a structure one of your two inferred rules
  might want to modify but must not. Your rule set must explain it.
- One example disambiguates the ORDER of composition — getting both rules
  right but composing them in the wrong order produces visibly different
  output there. Study it.

## Verification (f)
From the repo root:

```
python "avo-lab/checkers/x5_checker.py" "avo-lab/evals/tasks/x5-compose"
```

Grades each hidden grid exactly (~33/33/34 points). PASS requires 100/100.
Do not read anything under avo-lab/checkers/.
