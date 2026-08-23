# AVO Loop (v1) — Long-Horizon Execution Discipline

Derived from NVIDIA's Agentic Variation Operators (AVO). Core finding: the
harness around a model, not the model alone, converts capability into results.
Follow this loop mechanically. It is designed to be checkable, not aspirational.

**Principle:** every non-trivial task is evolutionary search over candidates.
A candidate that was never scored by real execution does not exist.
Failures are data. Memory lives on disk.

## 0 — State directory (your persistent memory)

Create `avo/` in the task root before anything else:

- `avo/LINEAGE.md` — append-only candidate ledger (format below)
- `avo/NOTES.md` — knowledge base: verified interface contracts, file paths,
  environment facts, gotchas. Only record what you verified. Mark anything
  unverified as `UNVERIFIED:`.

Rules: read `LINEAGE.md` before every candidate; write to it after every
evaluation; update `NOTES.md` the moment you learn a fact. Your context can be
compacted at any time; disk state survives.

Ledger row format (one row per candidate, appended in order):

```
| # | hypothesis | change made | eval cmd + real result | verdict | lesson |
```

`verdict` is COMMIT (new best score, or correctness restored) or REJECT.

## 1 — Ground (inspect context)

- Restate the goal in ≤3 lines. List explicitly what is NOT asked.
- Inventory what exists: relevant files, entry points, tests, configs.
- Unfamiliar environment with no instructions? Probe cheaply first: prefer the
  smallest safe action that reveals the most information. Record findings in
  NOTES.md before acting further.

## 2 — Evaluator first (f)

- Identify the command(s) that objectively decide success: test suite, checker
  script, compiler, benchmark. These are f.
- If none exists, WRITE f BEFORE writing the solution. f must print a score or
  pass/fail derived from execution.
- Run f on the untouched starting state and record it as candidate #0 baseline.
- Never grade your own work by reading it. Scores come from executed commands,
  output pasted verbatim into the ledger. An unexecuted claim is invalid.

## 3 — Candidate loop (the variation operator)

Each candidate is:

1. **Hypothesis** (one sentence): "Current state scores S / fails because X;
   changing Y should give ≥ S / restore correctness."
2. **ONE conceptual change per candidate.** One strategy, not five tweaks —
   otherwise score deltas are unattributable.
3. Implement minimally; match surrounding code style.
4. Run f. Paste the real output into the ledger row.
5. Verdict COMMIT/REJECT. On REJECT, write one-line lesson ("what this rules out").

## 4 — Diagnose before retry (repair budget)

Classify every failure before writing more code:

- **(a) Implementation bug** — right hypothesis, wrong code. Repair the same
  hypothesis. Maximum 2 repairs; beyond that treat as (b).
- **(b) Wrong hypothesis** — the idea itself fails. Abandon that direction.
  The next candidate MUST come from a different strategy family, chosen using
  ledger evidence (which families were tried, what each ruled out).

Never resubmit a rejected hypothesis unchanged. Never bundle multiple new ideas
into one rescue attempt.

## 5 — Self-supervision (stall detection)

- **3 consecutive REJECTs ⇒ STOP coding.** Re-read the original task. List your
  standing assumptions. Write down 2 alternative approach families you have NOT
  tried. Pick the one best supported by evidence so far. Resume there.
- **Budget/circuit breaker:** if the agreed attempt/time budget is spent, or 6
  total candidates have been REJECTed, STOP. Report honestly: best achieved
  score, winning candidate #, rejected directions + why each died, concrete
  recommended next step. Do not thrash past the breaker.

## 6 — Done means

- f executed green, real output pasted verbatim in ledger and summary
- LINEAGE.md complete for every candidate tried
- NOTES.md consistent with final state
- Final summary states: final score, winning candidate #, and rejected
  directions worth remembering.

If any item is missing, you are not done — say what remains instead of
claiming completion.
