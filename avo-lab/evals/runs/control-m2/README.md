# M2 — Cart with seeded defects (medium)

## Task
`cart.py` in this folder implements a shopping cart. It contains **exactly
three defects** relative to the correct specification below. Find and fix all
three. Do not change the public API (class name, method names, signatures,
return types). You may add private helpers.

## Correct behavior (the spec)

- `Cart()` — empty cart.
- `add(item_id, qty, unit_price)` — qty must be a positive int else `ValueError`.
  Adds a new item or increments an existing item's quantity; the stored
  `unit_price` becomes the latest one passed for that id.
- `remove(item_id)` — deletes the entry entirely. Unknown id → `KeyError`.
  A removed id must not influence totals afterwards.
- `set_quantity(item_id, qty)` — qty must be ≥ 1 else `ValueError`.
- `apply_coupon(code)` — valid codes: `SAVE10` → 10% off, `SAVE25` → 25% off.
  Invalid code → `ValueError`. Coupons stack MULTIPLICATIVELY and repeats are
  allowed: two SAVE10 coupons ⇒ factor 0.9 × 0.9 = 0.81.
- Bulk discount: if TOTAL units across all items ≥ 10, multiply by 0.95 once.
  Boundary: exactly 10 units qualifies.
- Computation order: subtotal = Σ qty×unit_price → apply each coupon factor →
  apply bulk factor if earned → round HALF UP to 2 decimals ONCE at the very end.
  No intermediate rounding anywhere.

## Verification (f)
From the repo root (hidden battery, 4 groups × several assertions):

```
python "avo-lab/checkers/m2_checker.py" "avo-lab/evals/tasks/m2-cart-bugs"
```

PASS requires 100/100. The checker imports your `cart.py`; it must import
cleanly and behave per spec. Do not read anything under `avo-lab/checkers/`.
