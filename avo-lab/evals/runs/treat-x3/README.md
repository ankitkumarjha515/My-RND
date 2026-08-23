# X3 — Warehouse inventory repair (hard)

## Task
`warehouse.py` implements an inventory ledger. It violates the behavioral
spec below in several places. Repair it so EVERY hidden rule holds.
Keep the public surface EXACTLY as-is:

```python
class Inventory:
    def __init__(self)
    def receive(self, sku: str, qty: int) -> None
    def reserve(self, sku: str, qty: int) -> int          # returns rid
    def release(self, sku: str, rid: int, qty: int) -> None
    def commit(self, sku: str, qty: int) -> None
    def available(self, sku: str) -> int
```

Internal representation is yours. Python stdlib only.

## Behavioral spec

- Quantities must be ints ≥ 1; unknown sku or bad qty raises `ValueError`.
  (Unknown sku raises ValueError — NOT KeyError.)
- `receive` adds on-hand stock.
- `reserve` reserves qty units IF `qty <= available(sku)`; appends a live
  reservation (with its own rid, unique per sku, starting at 1 and
  incrementing); returns the rid. Reservations cap availability.
- `release(sku, rid, qty)` returns qty units from that ONE reservation back
  to availability: the reservation shrinks by qty; if its remainder hits 0
  it disappears. Releasing more than the reservation's remaining size is
  capped at that remaining size (never errors). Unknown rid → ValueError.
  Released units are immediately reservable again.
- `commit(sku, qty)` requires `qty <= on_hand(stock)`; decrements on-hand by
  qty; then consumes LIVE reservations oldest-first (FIFO) up to qty units.
  If reservations total less than qty, the shortfall just comes off stock.
  Committed reservation entries vanish per FIFO consumption.
- `available(sku)` = on-hand − current live-reserved total, floor 0.
  It must ALWAYS reflect every operation above immediately.

## Why this is tricky (fair warning)

Several rules interact: a patch that fixes one visible symptom can silently
break another hidden one. The visible demo (`python demo.py`) shows ONE
symptom only. Passing the demo is necessary but nowhere near sufficient.

## Verification (f)
From the repo root (hidden battery, 4 weighted groups):

```
python "avo-lab/checkers/x3_checker.py" "avo-lab/evals/tasks/x3-warehouse"
```

PASS requires 100/100. Do not read anything under avo-lab/checkers/.
