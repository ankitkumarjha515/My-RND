# LINEAGE — treat-h2

| # | hypothesis | change made | eval cmd + real result | verdict | lesson |
|---|---|---|---|---|---|
| 0 | (baseline) no outputs written yet | none | `python "avo-lab\checkers\h2_checker.py" "avo-lab\evals\runs\treat-h2"` -> `FAIL grid-h1: missing file: outputs\h1_out.txt` / `FAIL grid-h2: missing file` / `FAIL grid-h3: missing file` / `SCORE 0/100 FAIL` | REJECT (baseline) | need outputs/h{1,2,3}_out.txt |
| 1 | Rule: fill a 4-connected zero-component with color c iff it touches no grid border AND all adjacent nonzero cells share value c (mixed surround -> untouched, per Ex4 negative case). Generalizes; no hardcoding. | Added solve.py implementing the rule; generated outputs/ for h1,h2,h3 | run 1: crash FileNotFoundError (outputs/ dir absent) -> repair: makedirs; run 2: `python "avo-lab\checkers\h2_checker.py" "avo-lab\evals\runs\treat-h2"` -> `OK grid-h1: exact match` / `OK grid-h2: exact match` / `OK grid-h3: exact match` / `SCORE 100/100 PASS` | COMMIT | single-color enclosure + border-touch exclusion explains all 4 examples incl. the deliberate negative case |
