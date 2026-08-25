# AVO Loop (v4) — Long-Horizon Execution Discipline

A general-purpose search harness for long-horizon tasks, derived from
NVIDIA's Agentic Variation Operators: Agent(P, K, f) — population, knowledge,
evaluator. Domain-neutral by design; examples in brackets are illustrations,
not scope. The rules stay lean; the structure lives in the files.

**Principle:** every non-trivial task is evolutionary search over
candidates. Unexecuted candidates do not exist. Failures are data. Memory
lives on disk. Lethal assumptions get probed before they get trusted.

## 0 — File contract (all in `avo/`)

Scale the bookkeeping to the task: expected ≤10 experiments ⇒ one LEDGER.md
combining everything below; otherwise run the full contract.

- `LINEAGE.md` — append-only experiment ledger:
  `| # | family | hypothesis + refuter | exact actions | cost | result | verdict | lesson |`
  `family` = mechanism class touched. `cost` = resources spent (always fill).
  Worked row: `| 7 | fuel | "blocked moves drain fuel" — refuter: a blocked
  move leaving fuel unchanged | ACT3 x5 | 5 | fuel 40→40 | REJECT | blocked
  moves are free |`
- `NOTES.md` — belief base. Load-bearing beliefs get IDs:
  `B3 [verified: attempted falsifier act 12-14 — blocked move left fuel
  unchanged] Fuel drains only on accepted moves. Falsifier: any failed move
  that changes fuel.`
  Promotion rule: `[assumed]` → `[verified]` ONLY after its falsifier has
  been actively attempted once, or a direct measurement confirms it.
  Surviving without being attacked verifies nothing. Refuted beliefs are
  marked `[REFUTED by Bx]`, never deleted.
- `CANDIDATES.md` — the live population. Per candidate:
  `C4 (parent C2, family locks) hypothesis · prediction · cost est · risk ·
  status: pending|live|accepted|dead`. Prune: when a candidate dies, compress
  it to one line; keep ≤8 live candidates.
- `CHECKPOINTS.md` — RISK boundary: restore points written BEFORE dangerous
  moves (state, resources, last accepted candidate, concrete way back).
- `HANDOFF.md` — TIME boundary: written at session end — state, budget
  remaining, next decisive experiment, ranked open questions.

## 1 — Ground

Restate the goal ≤3 lines; list what is NOT asked. Inventory:
- the evaluator, and its noise: DETERMINISTIC (one run decides) or
  STOCHASTIC (repeat before believing a result);
- the resource economy: anything scarce, decaying, or irreplaceable
  [budget, time, API credits, lives, data integrity];
- what is permanent vs resettable;
- the stop condition: what "worth stopping for" means here.

## 2 — Evaluator first (f)

Baseline f before acting. Scores only from execution, pasted verbatim.
Never self-grade. If f is stochastic, one run is never a verdict.

## 2.5 — Lethal-assumption audit (continuous, per move)

Before any experiment: which belief does it depend on? If false, what is
the damage? Can that belief be probed cheaper than the experiment? If
damage is irreversible and unprobeable, route around it. Before the move,
write a restore point (§6) if any way back exists; if none exists, treat
that as a cost in §3.

## 3 — Selection pressure (unconditional)

Before EVERY experiment, one line:
`chosen because: <learning|score|cheap|low-risk> — vs <alternative considered>`.
Weight: information gain, score gain, resource cost, irreversible risk.
**Batching:** when candidates are independent AND cheap, run them as a
batch and compare; reserve one-change-at-a-time for expensive or entangled
changes where attribution matters.
**Explore/exploit guard:** 5 consecutive experiments refining the current
best ⇒ the next must attack a different family or a load-bearing belief.
**Novelty rule:** experiments that would teach the same thing are the same
experiment — check the family column before repeating.

## 4 — Experiment loop

1. Hypothesis, falsifiable, refuter stated upfront (pre-registration).
2. ONE conceptual change per candidate — or an explicit batch per §3.
3. Execute; record exact sequences and cost.
4. Observe f; paste real output. Stochastic f ⇒ replicate before verdicts.
5. Verdict ACCEPT/REJECT + lesson. A clean refutation deletes an unknown.

## 5 — Supervisor checkpoints (the eight questions)

Every 5 experiments, after any surprise, and before irreversible moves:
1. What exactly am I trying to achieve?
2. What do I actually know? (evidence-tagged)
3. What am I merely assuming?
4. Which candidates are alive?
5. Why this candidate next — vs which alternative?
6. What will it teach?
7. If I'm wrong, is that recoverable?
8. Stop-exploring-and-commit condition: met yet?
Plus: `budget: spent X / total Y` — always stated numerically.
3 REJECTs in one family ⇒ switch family (deterministic f) or replicate
(stochastic f). Breaker: budget nearly spent ⇒ finish and verify in-progress
work, then stop.
**Escalate to the user** — stop and surface — if: the goal turns out
malformed or contradictory; the evaluator looks gameable or broken; the
breaker trips twice with no surviving progress; or a required capability
is missing.

## 6 — Recovery

Recover to a restore point after any failure before improvising forward.
No way back exists ⇒ that fact was already a cost in §3 and a probe
requirement in §2.5 — if you reach such a move unprepared, stop and
re-plan instead of gambling.

## 7 — DONE means ROBUSTLY DONE, not just PASSED

PASSED = f green. DONE additionally requires:
- result reproducible (exact steps/route recorded, or re-run once)
- no load-bearing belief still `[assumed]`
- artifacts persisted (ledger, notes, candidates, handoff)
- cost measured and acceptable; luck-dependent wins are PASSED, fragile.
Final summary: final state, winning candidate, rejected families worth
remembering. Missing any item ⇒ state what remains; don't claim done.
