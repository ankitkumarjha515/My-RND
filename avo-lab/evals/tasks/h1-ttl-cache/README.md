# H1 — TTL + LRU cache (hard)

## Task
Create `solution.py` in this folder defining:

```python
class TTLCache:
    def __init__(self, capacity: int, clock): ...
    def put(self, key, value, ttl=None) -> None: ...
    def get(self, key, default=None): ...
    def delete(self, key) -> bool: ...
    def clear(self) -> int: ...
```

Python 3 standard library only.

## Contract

- `clock` is an injected zero-argument callable returning float seconds
  (monotonic in tests). NEVER call a real time function.
- `capacity` must be an int ≥ 1 else raise `ValueError` at construction.
- Entry lifecycle: an entry with ttl is valid while `now < inserted_at + ttl`.
  At `now == expires_at` it is already EXPIRED (boundary is exclusive).
  `ttl=None` means never expires. Re-putting a key resets value, ttl and
  recency, using the CURRENT clock reading.
- `get(key, default)` — live entry: refresh its recency, return its value.
  Missing or expired: delete any expired entry encountered and return
  `default`. Expired entries must not count toward capacity afterwards.
- `put(key, value, ttl=None)`:
  1. If key exists but is expired, remove it first.
  2. If inserting a NEW key and size == capacity after step 1, evict the
     least-recently-used entry (LRU = least recently read via get OR written
     via put; construction order counts as initial recency order).
  3. Insert/update with recency = current time.
- `delete(key)` — True if a LIVE entry was removed; False if missing/expired
  (expired ones get removed too, without counting as True).
- `clear()` — removes everything (live and expired), returns how many entries
  were physically removed.
- Complexity: get/put/delete must be O(1) average. The perf group will fail on
  list-scan implementations.

## Verification (f)
From the repo root:

```
python "avo-lab/checkers/h1_checker.py" "avo-lab/evals/tasks/h1-ttl-cache"
```

Groups: basic ops (25), expiry semantics incl. boundary (30), LRU+eviction
order (30), performance 150k mixed ops ≤ 5s (15). PASS requires 100/100 —
any perf failure caps the run at FAIL regardless of correctness points.
Do not read anything under `avo-lab/checkers/`.
