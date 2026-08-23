# Eval round 1 — results summary (2026-08-22)

12 runs: 6 tasks × {control (no skill), treatment (SKILL.md v1 injected)}.
All scores below were re-verified by the orchestrator running the checkers
directly against each run folder — not taken from agent self-reports.

## Scores

| Task | Tier | Control | Treatment | Δ |
|---|---|---|---|---|
| e1-log-triage | easy | 100 PASS | 100 PASS | 0 |
| e2-csv-stats | easy | 100 PASS | 100 PASS | 0 |
| m1-brackets | medium | 100 PASS | 100 PASS | 0 |
| m2-cart-bugs | medium | 100 PASS | 100 PASS | 0 |
| h1-ttl-cache | hard | 100 PASS | 100 PASS | 0 |
| h2-grid-transform | hard | 100 PASS | 100 PASS | 0 |
| **Total** | | **600/600** | **600/600** | **±0** |

## Conclusion: ceiling effect — no measurable improvement

Every control agent solved every task on this suite. When the baseline is
perfect, score improvement is mathematically impossible; ±0 here is a property
of the eval suite, not evidence that the skill does nothing.

## What the treatment arm did demonstrate

1. **Process compliance 6/6**: all six treatment agents created avo/LINEAGE.md
   ledgers with baseline candidate #0 and COMMIT/REJECT verdicts, per skill.
2. **No degradation**: the added discipline cost nothing in outcomes.
3. **Observability asymmetry**: treatment runs left auditable trails
   (e.g., treat-m1 recorded REJECT → repair → COMMIT; treat-m2 committed one
   defect-fix per candidate). Control runs leave no comparable record — if a
   control had failed, diagnosing why would be guesswork.
4. Checker discrimination is proven independently: shipped buggy cart = 25/100,
   naive cache = 40/100, missing outputs = 0/100.

## Decision rule outcome (per rubric.md)

"Skill helps" requires treatment ≥ control AND fewer process violations.
Treatment ≥ control holds as a tie. Violation comparison is vacuous when no
run fails. **Verdict: indeterminate on this suite.**

## Required for a decisive round 2

Tasks with headroom where first-attempt failure is likely:
multi-file bugs with cross-module interactions, perf-constrained algorithms,
larger compositional inference puzzles, or deliberately underspecified tasks
where assumption management matters. Pilot them on 3 controls first; keep any
task where a control scores < 100 into the comparison set.
