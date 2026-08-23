# NOTES — treat-m2

## Verified facts
- Baseline checker output (candidate #0): SCORE 25/100 FAIL. Groups: has-cart OK, basic-ops OK, rounding-at-end FAIL, coupon-stacking FAIL, bulk-boundary FAIL.
- Candidate #1 (multiplicative coupons): coupon-stacking group green; SCORE 50/100.
- Candidate #2 (bulk gate ≥ 10): bulk-boundary group green; SCORE 75/100.
- Candidate #3 (exact Decimal pipeline, single terminal ROUND_HALF_UP): all groups green; **SCORE 100/100 PASS**.

## Final defect list (all fixed)
1. Coupons were combined additively with a hidden 50% cap (`factor -= min(sum(coupons), 0.5)`); spec requires multiplicative stacking with repeats (SAVE10 twice ⇒ ×0.81).
2. Bulk discount gate was exclusive (`total_units() > 10`); spec says exactly 10 units qualifies (`>= 10`).
3. Rounding violated spec twice over one defect area: per-line rounded `line_total` fed the subtotal (intermediate rounding), and final rounding used the float hack `int(raw*100+0.5)/100`, which is not reliable HALF UP on binary floats (e.g., x.xx5 values). Replaced with exact Decimal arithmetic end-to-end and one terminal quantize.

## Design decisions (UNVERIFIED beyond checker pass)
- `Decimal(str(value))` conversion chosen so decimal literals like 19.99 behave exactly as written; float noise never enters the computation path.
- Internal `line_total` dict key removed entirely (was unused after fix); public API untouched: Cart/add/remove/set_quantity/apply_coupon/total_units/total signatures and ValueError/KeyError behavior unchanged.
