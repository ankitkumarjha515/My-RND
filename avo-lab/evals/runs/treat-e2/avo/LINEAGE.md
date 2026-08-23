# LINEAGE — treat-e2

| # | hypothesis | change made | eval cmd + real result | verdict | lesson |
|---|---|---|---|---|---|
| 0 | Baseline: untouched starting state (no stats.json yet) fails checker | none | `python "avo-lab\checkers\e2_checker.py" "avo-lab\evals\runs\treat-e2"` → `FAIL json-parses: stats.json missing / FAIL total-orders: / FAIL revenue-by-region: / FAIL grand-total: / FAIL top-product: / SCORE 0/100 FAIL` | REJECT (baseline) | Must create stats.json to move at all. |
| 1 | Exact Decimal sums from raw CSV strings; ROUND_HALF_UP quantize once at end; JSON numbers as decimal tokens | created `avo/compute.py` + `stats.json` (total_orders=48, north 2441.55, south 4799.71, east 5760.76, west 4241.68, top_product chair qty 156, grand_total 17243.70) | `python "avo-lab\checkers\e2_checker.py" "avo-lab\evals\runs\treat-e2"` → `OK json-parses: / OK total-orders: expected 48 / OK revenue-by-region: expected {'north': 2441.55, 'south': 4799.71, 'east': 5760.76, 'west': 4241.68} / OK grand-total: expected 17243.7 / OK top-product: expected 'chair' / SCORE 100/100 PASS` | COMMIT | Decimal-from-string + single end-rounding matches half-up rule exactly. |
