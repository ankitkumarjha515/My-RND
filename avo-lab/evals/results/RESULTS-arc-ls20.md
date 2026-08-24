# ARC-AGI-3 experiment — ls20, results (2026-08-23)

First real-benchmark test of SKILL.md v1 vs no-skill, via the official
arc-agi toolkit (local environments, anonymous key). Game: ls20 (7 levels,
human baseline 22/123/73/84/96/192/186 = 676 total actions).
Budget per arm: 80 actions/session. Driver: avo-lab/arc/driver.py
(persistent background server + file-channel client, verified stateful).

## Outcomes

| Metric | Control (no skill) | Treatment (AVO skill) |
|---|---|---|
| Total levels after 160 actions | **1/7** | **1/7** |
| Level 1 first solve cost | 66 actions | 66 actions |
| Level 1 re-solve cost (session 2) | 35 (28-action replay) | 0 (never left L2) |
| Memory artifacts | ~50 loose unannotated frame files in root | avo/LINEAGE.md (11+ experiments), avo/NOTES.md, 80 annotated frames, frame-diff tooling (diff.py/scan.py) |
| Mechanic model at end | maze, 5-cell moves, walls, door-bump unlock, input buffering | + rotator-glyph semantics (4 rotations, variant C), life-meter decay, flood/respawn, terrain rules, b-diamond refills |
| Self-correction of knowledge | n/a (no written knowledge) | found its OWN stale fact (decay is -2/action incl. failed moves, not ~1/successful), corrected NOTES.md, re-derived route math |
| End state | L2: mapped rails, found pickups, no mechanism | L2: arithmetic proof that one life cannot cover rotations + box-2 route (>=16 short), decisive 11-action experiment queued for next session |

## What the data says

1. Outcome tie at 1/7 - but the binding constraint is BUDGET, not
   intelligence: humans need 676 actions; we gave each arm 160 (24%).
   Level 2 alone has a human baseline of 123.
2. The skill's effect showed exactly where AVO predicts - in MEMORY and
   RECOVERY, not in one-shot brilliance:
   - Control's unstructured memory required "archaeology" (frame diffing,
     re-deriving the action grammar, ~20 actions re-learning movement rules).
   - Treatment's structured ledger let it skip re-solve entirely, correct
     its own recorded physics error, and convert 28 actions into a precise
     next-session plan.
3. Both arms converged on identical level-1 solve cost (66) in session 1 -
   deterministic game, same model, similar exploration instincts.

## Caveats (disclosed)

- A cancelled launch left the treatment server mid-game at step 52; its
  "session 2" was a continuation (log verified: unbroken 0-80). This favors
  demonstrating memory value but breaks the clean restart-restart symmetry.
- Treatment's session-1 report mentioned learning from "a previous session's
  frame logs"; both dirs are siblings and control's raw frames were readable.
  Unproven whether cross-run peeking occurred; identical 66-step solves
  suggest no decisive transfer, but future runs should isolate dirs.
- n=1 per arm, same underlying model both arms.
- Control spontaneously adopted note-taking in session 2 (wrote NOTES.md) -
  by then it had effectively reinvented part of the skill.

## Next decisive step

Run the treatment's queued 11-action experiment (session 3). If box-2
unlocks -> 2/7, first outcome break of the tie, and evidence of compounding
memory value. Symmetry requires a control session 3 as well.

## Session 3 addendum (same day)

Both arms continued mid-L2 (steps 79/80). Both terminated by the game's
PERMANENT GAME_OVER: lives are finite and cumulative across sessions - the
flood-respawn rule both arms had recorded only holds while lives remain.

- Control: reached step 121. Independently built a BFS pathfinder over its
  saved frames, proved dip-editing cycles source-room band patterns, died
  on arithmetic (pad is 17 presses from respawn, ~1 surplus move per life).
  Left open question: do band edits survive soft reset?
- Treatment: executed its queued 11-action experiment EXACTLY as planned
  from notes alone (route geometry flawless) -> CLEAN REFUTATION: keyless
  box-2 entry impossible, rotated key glyph required. Bonus finds: diamonds
  exist on upper L2 (+28 meter), mouth-bump proximity indicator. Fatal gap,
  self-identified: never stress-tested the assumption that dying was free.
  Left feasibility math (~13 acts per rotation pass) for a future game.

Outcome after 3 sessions: still tied 1/7 - permadeath + energy economy +
per-session budgets walled level 2 for both arms. Convergence: by session 3
control had organically adopted notes + tools, narrowing the process gap.
The skill's durable advantages: immediate structure (sessions 1-2), exact
plan execution from memory, disciplined hypothesis refutation.
