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

## v3 - 2026-08-24
External review (8.8/10) + field evidence from ls20 rematch. Upgrades:
- File contract: CANDIDATES.md population (parent/family/status) and
  CHECKPOINTS.md restore points join LINEAGE/NOTES/HANDOFF.
- Selection pressure: explicit choose-because line (learning + gain - cost
  - risk vs alternatives); explore/exploit guard; novelty rule via family
  column (informationally identical experiments are the same experiment).
- Belief management: load-bearing beliefs get IDs + falsifiers; refuted
  beliefs marked, never deleted.
- Lethal-assumption audit promoted from one-time checklist to continuous
  per-move reflex (dependence, damage, cheaper probe).
- Recovery: RESTORE points before irreversible actions; no-way-back raises
  the evidence bar; recover-to-point after failure instead of improvising.
- DONE vs PASSED split: reproducibility, no assumed load-bearing beliefs,
  known cost. Fragile wins are PASSED, not DONE.
- Supervisor checkpoint = the eight questions (compact self-audit).
Deliberately NOT adopted: longer prose, literal math formula, separate
world-model file. Skill kept ~150 lines; structure lives in artifacts.
Backup: backups/SKILL.v3.md.

## v4 - 2026-08-24
Second external review (7/10, mechanical-read) - all 8 findings addressed:
- Falsifier promotion rule: [assumed]->[verified] requires the falsifier to
  have been ACTIVELY attempted once (passive survival verifies nothing).
- Domain leak fixed: general-purpose vocabulary committed (fuel/lives/
  frame-perfect demoted to bracketed illustrations).
- Budget accounting: cost column in LINEAGE (worked example added),
  numeric spent/total at every checkpoint, budget-remaining in HANDOFF.
- Batching clause: independent + cheap candidates run as a batch; serial
  isolation reserved for expensive/entangled changes.
- Scaling clause: <=10 expected experiments collapses to a single LEDGER.
- Noise clause: evaluator classified deterministic/stochastic at Ground;
  stochastic results replicated before verdicts; 3-reject rule branches.
- Selection line made unconditional (no obvious escape hatch).
- CHECKPOINTS (risk boundary) vs HANDOFF (time boundary) split; candidate
  pruning (<=8 live, dead compressed); escalate-to-user triggers added.
Backup: backups/SKILL.v4.md.
