# E2 — CSV revenue stats (easy)

## Input
`sales.csv` in this folder with header:

```
order_id,region,product,quantity,unit_price
```

- `unit_price` may have up to 3 decimal places.
- `quantity` is a positive integer.

## Task
Create `stats.json` in this folder — a single JSON object with exactly these keys:

```json
{
  "total_orders": <int, number of data rows>,
  "revenue_by_region": {"north": x.xx, "south": x.xx, "east": x.xx, "west": x.xx},
  "top_product": "<product name>",
  "grand_total": x.xx
}
```

Rules:

- Revenue per region = sum over that region's rows of `quantity * unit_price`.
- `grand_total` = sum of all rows' `quantity * unit_price`.
- Round HALF UP to exactly 2 decimals, applied ONCE at the end (never per-row).
  All four regions appear in the output even if a region has no rows (value 0).
- `top_product` = product with the highest total quantity; exact tie →
  alphabetically first name.
- Numbers must be JSON numbers (not strings).

## Verification (f)
From the repo root:

```
python "avo-lab/checkers/e2_checker.py" "avo-lab/evals/tasks/e2-csv-stats"
```

PASS requires 100/100. Note: naive float rounding is not half-up rounding.
