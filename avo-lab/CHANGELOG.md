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
