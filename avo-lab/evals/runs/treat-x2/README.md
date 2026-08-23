# X2 — Ten-constraint report (hard)

## Input data (authoritative — 12 rows)

| region | product | units | unit_cost |
|---|---|---|---|
| north | anvil | 4 | 12.505 |
| south | bolt | 11 | 0.355 |
| east | crate | 7 | 4.10 |
| west | dowel | 2 | 1.115 |
| north | bolt | 6 | 0.355 |
| east | anvil | 3 | 12.505 |
| west | crate | 9 | 4.10 |
| south | dowel | 5 | 1.115 |
| north | crate | 8 | 4.10 |
| east | bolt | 12 | 0.355 |
| west | anvil | 1 | 12.505 |
| south | crate | 10 | 4.10 |

Revenue per row = units * unit_price where unit_price = unit_cost * 1.5
(markup). Round only at the end, HALF UP, 2 decimals.

## Task
Create exactly two files in this folder: `report.json` and `report.txt`.
They must satisfy ALL TEN constraints below. Each is worth 10 points.

- C1. `report.json` parses; its top-level keys are EXACTLY
  `["meta", "totals", "regions", "top_products"]` in that exact order.
- C2. `meta` equals `{"generated_by": "AVO-R2", "source_rows": 12}`.
- C3. `totals.grand_revenue` is the grand total revenue, HALF-UP rounded to
  exactly 2 decimal places (a JSON number).
- C4. `totals.units_total` is the integer sum of all units.
- C5. `regions` maps EVERY distinct region name to its revenue (same rounding)
      and its keys appear in REVERSE alphabetical order (descending, z first).
- C6. `top_products` is a list of the 3 product names with highest TOTAL
      revenue across regions, highest first; exact revenue ties broken by
      alphabetical product name (ascending).
- C7. `report.txt` has exactly 6 lines separated by `\n`, and a single final
      newline after line 6.
- C8. Line 3 of report.txt is exactly `---`.
- C9. Line 1 is exactly `TOTAL: <grand_revenue> USD` using the same value as
      C3. TERMINAL CONSTRAINT: the very last character of the file is `%`,
      and line 6 starts with `MARGIN ` followed by an integer percent:
      west-region units divided by total units, times 100, HALF-UP to int.
- C10. report.txt contains NO comma characters and NO lowercase letters
       anywhere (uppercase letters, digits, spaces, punctuation allowed).

## Verification (f)
From the repo root:

```
python "avo-lab/checkers/x2_checker.py" "avo-lab/evals/tasks/x2-constraints"
```

Prints one OK/FAIL line per constraint C1..C10, then SCORE x/100.
