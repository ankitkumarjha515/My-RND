# AVO Loop (v3) — Long-Horizon Execution Discipline

Derived from NVIDIA's Agentic Variation Operators: Agent(P, K, f).
v3 upgrades the discipline from a loop into a search architecture:
candidate population, explicit selection pressure, belief management,
recovery points, and robust-done criteria. The rules stay lean; the
structure lives in the files.

**Principle:** every non-trivial task is evolutionary search over
candidates. Unexecuted candidates do not exist. Failures are data.
Memory lives on disk. Lethal assumptions get probed before they get trusted.

## 0 — File contract (all in `avo/`, created before anything else)

- `LINEAGE.md` — append-only experiment ledger:
  `| # | family | hypothesis + refuter | exact actions | result | verdict | lesson |`
  `family` = mechanic family (e.g. `movement`, `fuel`, `locks`). Exact
  sequences, never summaries.
- `NOTES.md` — belief base. Load-bearing beliefs get IDs:
  `B3 [verified: acts 12-14] Fuel burns -2/action incl. failed moves.
   Falsifier: a failed move that leaves fuel unchanged.`
  Mark `[assumed]` and `[REFUTED by B9]`; never delete refuted beliefs.
- `CANDIDATES.md` — the live population. One block per candidate:
  `C4 (parent C2, family locks) hypothesis · predicted outcome · cost est ·
   risk · status: pending|live|accepted|dead`
  Candidates compete; you are not a chain, you are a population.
- `HANDOFF.md` — session-end state + next decisive experiment.
- `CHECKPOINTS.md` — restore points (see §6).

## 1 — Ground

Restate the goal ≤3 lines; list what is NOT asked. Inventory: evaluator,
resource economy (measure costs, update constants on contradiction),
permanent-vs-resettable state, and the win/stop condition.

## 2 — Evaluator first (f)

Baseline f before acting. Scores only from execution, pasted verbatim.
Never self-grade.

## 2.5 — Lethal-assumption audit (continuous)

Before ANY experiment: what belief does it depend on? If that belief is
false, what is the damage? Can the belief be probed cheaper than the
experiment? If damage is irreversible and unprobeable, route around it.
This is not a one-time checklist — it is a per-move reflex.

## 3 — Selection pressure (choose like a breeder, not a wanderer)

Before each experiment, when the choice is not obvious, answer one line:
`chosen because: learning X / score Y / cheap / low-risk — vs alternative Z`.
Weight four factors: expected information gain, expected score gain,
resource cost, irreversible risk. Never pick an experiment just because it
is next in a sequence.

**Explore/exploit guard:** if the last 5 experiments all refined the current
best candidate, the next one must attack a different family OR a load-bearing
assumption. Local optima kill long searches.

**Novelty rule:** two experiments are the same experiment if they would
teach the same thing. Check the family column before repeating.

## 4 — Experiment loop

1. Hypothesis, falsifiable, with its refuter stated upfront.
2. ONE conceptual change per experiment.
3. Execute; record exact sequences.
4. Observe f; paste real output.
5. Verdict ACCEPT (candidate survives) / REJECT (dies, lesson recorded).
   A clean refutation is a win — it deletes an unknown.

## 5 — Supervisor checkpoints (the eight questions)

Every 5 experiments, after any surprise, and before any irreversible move,
answer in one pass:
1. What exactly am I trying to achieve?
2. What do I actually know? (evidence-tagged)
3. What am I merely assuming?
4. What candidate approaches are alive right now?
5. Why am I testing this candidate next?
6. What will this experiment teach me?
7. What happens if I'm wrong — and is that recoverable?
8. When do I stop exploring and commit?
3 consecutive REJECTs ⇒ switch family. Budget nearly spent ⇒ finish and
verify in-progress work, then stop. Never thrash past the breaker.

## 6 — Recovery (RESTORE points)

Before any irreversible or expensive action, write a restore point in
`CHECKPOINTS.md`: current state, resources, last accepted candidate, and the
concrete way back to it. If there is NO way back, that fact raises the
required evidence bar (§2.5) — probe harder or route around. After any
failure, recover to a restore point before improvising forward.

## 7 — Done means ROBUSTLY DONE, not just PASSED

PASSED = f green. DONE requires additionally:
- final state valid and reproducible (route/steps recorded exactly)
- no load-bearing belief still `[assumed]`
- artifacts persisted (ledger, notes, candidates, handoff)
- cost known and acceptable (a lucky, frame-perfect, one-life-left win is
  not DONE — it is PASSED and fragile)
Final summary: final score/state, winning candidate, rejected families
worth remembering. Missing any item ⇒ say what remains, don't claim done.
