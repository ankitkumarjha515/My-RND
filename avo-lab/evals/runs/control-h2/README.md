# H2 — Infer the grid rule (hard, ARC-style)

## Task
`examples.txt` shows four worked transformations (INPUT grid → OUTPUT grid).
The transformation rule is deliberately NOT documented here. Infer it from the
examples, then apply it to the three unseen inputs in `inputs/`.

Write each transformed grid to:

```
outputs/h1_out.txt
outputs/h2_out.txt
outputs/h3_out.txt
```

(create the `outputs/` folder). Same text format as the inputs: one row per
line, integer cell values separated by single spaces, dimensions preserved.

## Rules of the game

- Your solution must GENERALIZE from the examples. Hardcoding coordinates or
  memorizing example answers will score zero on the unseen grids.
- If two rules fit the examples, prefer the simplest one consistent with ALL
  four examples. One example contains a deliberate negative case (a region the
  rule does NOT modify) — your inferred rule must explain why.

## Verification (f)
From the repo root:

```
python "avo-lab/checkers/h2_checker.py" "avo-lab/evals/tasks/h2-grid-transform"
```

Grades each of the 3 output grids (exact match against the true rule,
~33 points each). PASS requires 100/100.
Do not read anything under `avo-lab/checkers/`.
