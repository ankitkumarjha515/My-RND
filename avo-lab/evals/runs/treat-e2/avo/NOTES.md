# NOTES — treat-e2

## Verified facts
- sales.csv: header `order_id,region,product,quantity,unit_price`; 48 data rows (order_id 1000–1047); regions present: east, south, west, north; products: desk, lamp, chair, shelf.
- unit_price values have up to 3 decimals (e.g. 36.382, 25.000).
- README rules: region revenue = sum(qty*price) per region; grand_total = sum all rows; HALF-UP rounding to exactly 2 decimals applied ONCE at end (never per-row); all four regions present even if empty (0); top_product = highest total quantity, tie → alphabetically first; numbers must be JSON numbers.
- Baseline f run (candidate #0): `SCORE 0/100 FAIL` — stats.json missing.

## Approach (candidate #1)
- Parse CSV with csv.DictReader; compute sums in `decimal.Decimal` built from the raw strings (exact, no float error), ROUND_HALF_UP quantize to 0.01 only at output time.
- Emit JSON with numbers as raw decimal tokens (str of quantized Decimal) to avoid float artifacts; validate file parses via json.loads before declaring done.

## Guesses (UNVERIFIED)
- (resolved) Checker compares parsed numeric values; exact 2-dp tokens accepted.

## Final state
- Candidate #1 COMMIT: `SCORE 100/100 PASS`.
- Final verification output:
  ```
  OK   json-parses:
  OK   total-orders: expected 48
  OK   revenue-by-region: expected {'north': 2441.55, 'south': 4799.71, 'east': 5760.76, 'west': 4241.68}
  OK   grand-total: expected 17243.7
  OK   top-product: expected 'chair'
  SCORE 100/100 PASS
  ```
- Rejected directions worth remembering: none — no hypothesis failed; only baseline (#0) was rejected for missing output file.
