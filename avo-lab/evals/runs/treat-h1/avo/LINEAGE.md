# LINEAGE — treat-h1

| # | hypothesis | change made | eval cmd + real result | verdict | lesson |
|---|---|---|---|---|---|
| 0 | Starting state has no solution, so f must fail with 0 points | none (baseline) | `python "avo-lab\checkers\h1_checker.py" "avo-lab\evals\runs\treat-h1"` → `FAIL imports: solution.py missing` … all groups FAIL, `SCORE 0/100 FAIL` | REJECT (baseline) | f works; checker expects solution.py importable from this folder |
| 1 | Dict key→node + sentinel doubly-linked list (recency = list position, precomputed expires_at, expired iff now >= expires_at) satisfies all 4 groups incl. O(1) perf | created solution.py implementing full TTLCache contract; pre-eval self-review repaired delete() to test expiry before removal | `python "avo-lab\checkers\h1_checker.py" "avo-lab\evals\runs\treat-h1"` → `perf: 0.43s for 150k mixed ops (cap=50000)` / OK has-ttlcache, basic-ops, expiry-semantics, lru-eviction, performance / `SCORE 100/100 PASS` | COMMIT | Literal spec reading + position-based LRU passed every group first try; perf 0.43s vs 5s budget |

