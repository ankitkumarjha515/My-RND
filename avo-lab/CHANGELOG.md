# avo-lab CHANGELOG

All skill versions. `backups/SKILL.vN.md` is the immutable copy of each version.
Never edit files in `backups/`. Rollback = copy a backup over `SKILL.md`.

## v1 — 2026-08-22
- Initial translation of NVIDIA AVO architecture into agent-process form.
- Mechanisms: disk-backed lineage ledger + notes (persistent memory),
  evaluator-first rule, one-hypothesis-per-candidate loop with COMMIT/REJECT
  verdicts, repair budget (2) + strategy-family switching on wrong hypotheses,
  self-supervision stall rules (3 consecutive rejects → forced strategy shift;
  6 total / budget → honest stop), done-checklist tied to executed evidence.

## v2 - 2026-08-23
Field-tested changes from ARC-AGI-3 ls20 autopsy (3 sessions, both arms):
- NEW 2.5 lethal-assumption audit: cheap-probe irreversible/costly assumptions
  before building on them (treatment death: never tested "dying is free").
- Resource economy moved into Ground: measured costs, permanent-vs-resettable
  state tracking (both arms' route math died on wrong decay constants).
- NOTES evidence tags [verified]/[assumed]/[REFUTED] - refuted facts are
  marked, never deleted (wrong beliefs recur otherwise).
- Experiments must state refutation conditions upfront; exact replayable
  action sequences in ledger (11-move flawless replay proved the value).
- Supervisor checkpoints broadened beyond stalls: stale load-bearing facts,
  riskiest untested assumption, budget drift - every 5 experiments.
- NEW session end protocol: mandatory avo/HANDOFF.md (state + next decisive
  experiment + ranked open questions).
- Clean refutations reframed as wins (unknown -> known).
Backup: backups/SKILL.v2.md. v1 remains in backups/SKILL.v1.md.
