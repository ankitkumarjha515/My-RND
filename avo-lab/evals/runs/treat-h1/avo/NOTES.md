# NOTES — treat-h1 (H1 TTL+LRU cache)

Verified facts:
- f = `python "avo-lab\checkers\h1_checker.py" "avo-lab\evals\runs\treat-h1"` from repo root. Groups: basic-ops(25), expiry-semantics(30), lru-eviction(30), performance(15, ~30s). PASS = 100/100.
- Candidate #0 (no solution.py): FAIL, SCORE 0/100.
- Design chosen: dict key→node + sentinel doubly-linked list ordered by recency (MRU at head). All ops O(1) average; no clock-order reliance for LRU (list position IS recency).
- Expiry rule: expired iff `expires_at is not None and now >= expires_at` (boundary exclusive-valid → at == it is dead).
- Store precomputed `expires_at = now + ttl` at put time; ttl=None ⇒ never expires.
- put literal algorithm: (1) same-key-expired removal first; (2) if NEW key and len==capacity → evict tail.prev (LRU, whatever its expiry state); (3) insert/update with recency=now. Size counts physically present entries incl. not-yet-touched expired ones (spec: "Expired entries must not count toward capacity afterwards" only after they are deleted on encounter).
- get-hit refreshes recency; get miss/expired deletes the expired node physically and returns default. delete: live→True (+remove), expired→remove but False. clear(): wipe map + list, return physical count.
- capacity validation: `not isinstance(capacity, int) or capacity < 1` → ValueError (bool is an int subclass; left allowed — UNVERIFIED edge).

UNVERIFIED guesses:
- Whether checker tests mixed live/expired-at-capacity eviction divergence (purge-first vs literal). Chose literal spec reading — RESOLVED: literal reading passed all groups (candidate #1, 100/100).

Final state:
- Candidate #1 COMMIT: SCORE 100/100 PASS, perf 0.43s / 5s budget. No rejected strategy families besides baseline.
