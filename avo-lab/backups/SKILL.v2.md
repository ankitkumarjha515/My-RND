# AVO Loop (v2) — Long-Horizon Execution Discipline

Derived from NVIDIA's Agentic Variation Operators: Agent(P, K, f) — lineage,
knowledge, evaluator. v2 adds what field testing (ARC-AGI-3 ls20, 3 sessions)
showed v1 lacked: lethal-assumption audits, resource accounting, evidence-tagged
knowledge, and mandatory session handoffs.

**Principle:** every non-trivial task is evolutionary search over candidates.
A candidate never scored by real execution does not exist. Failures are data.
Memory lives on disk. Assumptions that can kill you get tested first.

## 0 — State directory (persistent memory)

Create `avo/` in the task root before anything else:

- `avo/LINEAGE.md` — append-only experiment ledger, one row per experiment:
  `| # | hypothesis | exact actions/changes taken | observed result | verdict | lesson |`
  Record action sequences EXACTLY (replayable), never summarized.
- `avo/NOTES.md` — knowledge base. Every fact carries an evidence tag:
  `[verified: how]`, `[assumed]`, `[REFUTED: what replaced it]`.
  Never delete refuted facts — mark them; wrong beliefs recur otherwise.

Read both before deciding; write immediately after observing.

## 1 — Ground (inspect context)

- Restate the goal in ≤3 lines; list what is NOT asked.
- Inventory: relevant files/features; the evaluator; **the resource economy** —
  anything scarce, decaying, or irreplaceable (lives, energy, time, money,
  budget). Record measured costs, not guessed ones, and update constants the
  moment observation contradicts them.
- Record what is PERMANENT vs RESETTABLE in this environment.

## 2 — Evaluator first (f)

- Identify the command(s)/signals that objectively decide progress.
- Run f on the untouched starting state; record candidate #0 baseline.
- Scores come only from executed runs, pasted verbatim. Never self-grade.

## 2.5 — Lethal-assumption audit (before committing resources)

List assumptions whose failure is EXPENSIVE or IRREVERSIBLE (death, permanent
loss, dead ends, wasted budgets). For each: design the CHEAPEST probe that
tests it, and run those probes BEFORE building plans on top of the assumption.
An assumption that would cost a life if wrong is worth one early action to
test. Re-audit whenever you are about to do something unrecoverable.

## 3 — Experiment loop (the variation operator)

Each experiment:
1. **Hypothesis** — one sentence, falsifiable: "doing X will produce Y."
   State what observation would REFUTE it.
2. **ONE conceptual change** per experiment — attribution requires isolation.
3. Execute with EXACT sequences recorded.
4. Observe f. Paste real output into the ledger.
5. Verdict KEEP/REJECT + one-line lesson. A clean refutation is a WIN —
   it converts a unknown into a known. Extract the next question it raises.

## 4 — Diagnose before retry

- (a) Execution slip (right idea, wrong execution) → repair same hypothesis,
  max 2 retries, then treat as (b).
- (b) Wrong hypothesis → abandon the direction; the next experiment MUST come
  from a different mechanic family, chosen from ledger evidence.
- (c) Wrong ASSUMPTION behind the failure → add it to the 2.5 audit list and
  probe it. Never resubmit a rejected hypothesis unchanged; never bundle
  multiple new ideas into one rescue attempt.

## 5 — Supervisor checkpoints (conditional intervention)

Run this audit every 5 experiments OR after any surprise:
1. Stall? (3 consecutive REJECTs ⇒ stop, re-read the goal, list 2 untried
   approach families, pick one.)
2. Stale? Which load-bearing fact in NOTES.md is most likely wrong? Cheaply
   re-verify the one your current plan depends on.
3. Riskiest untested assumption right now? Probe it or route around it.
4. Budget: % spent vs % of plan completed — replan if badly off.
Circuit breaker: budget nearly spent ⇒ finish/verify in-progress work, then
stop. Never thrash past the breaker.

## 6 — Session end protocol (handoff)

Before stopping — budget spent, done, or interrupted — write
`avo/HANDOFF.md`:
- current state (where you are, what's in progress, resources remaining)
- the single next decisive experiment, with its exact planned sequence
- open questions ranked by value
The next session (possibly you with empty context) resumes from HANDOFF.md.

## 7 — Done means

f executed green with real output pasted · LINEAGE complete · NOTES evidence-
tagged · HANDOFF.md current · final summary states final score/state, winning
approach, and rejected directions worth remembering. Missing any item ⇒
you are not done — say what remains.
