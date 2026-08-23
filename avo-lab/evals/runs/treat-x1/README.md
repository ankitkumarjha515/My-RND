# X1 — Zigbus protocol interpreter (hard)

## Task
Create `interpreter.py` in this folder defining:

```python
def run(events: list[str]) -> list[str]:
```

Pure standard library. It interprets Zigbus wire events (strings) in order and
returns the exact transcript (list of output lines, no trailing whitespace).

## Protocol state

- `state` ∈ {DOWN, UP, WAIT}, initially DOWN
- `seq`, an integer 0..65535, initially 0
- `oflow` flag, initially 0
- `key`: the session key from the most recent successful OPEN

## Events and exact semantics

Process each event string (split on single spaces). Rules are listed in
priority order — the FIRST matching rule fires and no other:

### OPEN k
1. If `k` is not a valid key (exactly 4 chars, each in 0-9 A-F, uppercase
   only) → emit `ERR BAD-KEY`. State unchanged.
2. Else if `state != DOWN` → emit `ERR BUSY`. State unchanged.
3. Else: start session — state=UP, seq=0, oflow=0, key=k → emit `WELCOME`.

### SEND n
1. If `n` is not a decimal integer token (optional leading `-` forbidden;
   digits only) OR parses below 0 → emit `ERR BAD-N`. State unchanged.
2. Else if `state == UP`:
   - Compute `total = seq + n` and `new = total % 65536`.
   - If `total >= 65536` (the addition crossed one or more wrap boundaries)
     set `oflow = 1`.
   - `seq = new`.
   - If `oflow == 1` → emit `NAK OFLOW` (seq still advances!).
   - Else emit `ACK <seq>` (the NEW value).
3. Else if `state == WAIT` → emit `DEFERRED` (nothing else changes).
4. Else (DOWN) → emit `ERR CLOSED`.

### PARK
1. If `state == DOWN` → emit `ERR CLOSED`.
2. Else: state=WAIT → emit `PARKED` (idempotent when already WAIT).

### RESUME k
1. If `k` invalid (same key rules as OPEN) → emit `ERR BAD-KEY`.
2. Else if `state == DOWN` → emit `ERR CLOSED`.
3. Else if `state == UP` → emit `ERR ACTIVE`.
4. Else if `k == key` (case-sensitive) → state=UP → emit `RESUMED`.
5. Else → emit `ERR BAD-KEY` (state stays WAIT; session key unchanged).

### RESET
Any state: state=DOWN, seq=0, oflow=0, key=None → emit `RESET-OK`.

### CLOSE
1. If `state == DOWN` → emit NOTHING at all for this event.
2. Else: state=DOWN (key, seq, oflow are NOT cleared here) → emit `BYE`.

### Any other first token
Emit `ERR UNKNOWN`.

## Footer
After the last event, append exactly one line: `SEQ <seq> OFLOW <oflow>`
where `<oflow>` is 0 or 1. This line appears even for an empty event list.

## Verification (f)
From the repo root (hidden battery of 20 sequences in 5 groups):

```
python "avo-lab/checkers/x1_checker.py" "avo-lab/evals/tasks/x1-protocol"
```

PASS requires 100/100. Every rule above matters; several interact.
