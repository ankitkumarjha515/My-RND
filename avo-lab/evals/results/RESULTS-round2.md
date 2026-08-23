# Eval round 2 — results summary (2026-08-22)

Suite: 5 new tasks designed from failure-mode research (DESIGN-round2.md),
hardware-light (<1s CPU each), self-tested before use
(positive battery 5/5 = 100 PASS; negative battery incl. shipped-defective
warehouse = 45/100 FAIL).

## Control arm (no skill) - orchestrator-verified scores

| Task | Tests | Result |
|---|---|---|
| x1-protocol | 20 hidden sequences, priority rules, sticky flags | 100 PASS |
| x2-constraints | 10 stacked constraints incl. terminal | 100 PASS |
| x3-warehouse | root-cause repair, coherence-trap | 100 PASS |
| x4-corpus | exact char-level statistics over 13 KB corpus | 100 PASS |
| x5-compose | two-rule compositional inference | 100 PASS |

Total: **500/500**. Treatment arm NOT run: with every control at 100,
score improvement is impossible (max delta = 0). Pre-registered rule from
RESULTS-round1.md: only tasks with control headroom enter comparison.
Zero qualify.

## Qualitative observations (controls, from their own reports)

- x3 agent made exactly the predicted interaction mistake: read the blanket
  "unknown sku raises ValueError" rule too broadly, broke available(), saw
  the checker group flip to FAIL, reverted precisely. The checker caught it.
- x1 agent wrote its own throwaway test expectations and made three mistakes
  THERE while the implementation passed first-run.
- x2 agent found the genuine tension between C7 (trailing newline required)
  and C9 (last char %) and resolved it correctly via the rstrip-tolerant
  reading.
- x4 agent noticed CRLF line endings unprompted and canonicalized before
  counting.

## Emerging conclusion (two rounds of evidence)

With a frontier-class model, an executable evaluator, and short-horizon
single-file tasks, baseline performance saturates EVERY difficulty tier we
can construct cheaply - including research-targeted failure modes, because
the checker-in-the-loop converts those failure modes into recoverable
iteration. This matches NVIDIA's own framing inverted: harness advantages
(memory persistence, stall supervision) pay off when horizons exceed what a
single context can hold, not on 5-minute tasks.

To measure the skill's effect we would need to change the experiment axis,
not the difficulty number:
(a) campaign-length tasks (dozens of interlocking stages spanning many
    context windows), or
(b) weaker model backends for sub-agents (if configurable), or
(c) accept and document that in this regime the skill is process hygiene
    with zero measurable cost/benefit.
