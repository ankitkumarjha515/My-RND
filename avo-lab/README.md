# avo-lab — AVO skill laboratory

Empirically tests whether NVIDIA's AVO architecture, translated into a text
skill (`SKILL.md`), measurably improves sub-agent task performance.

**Stage gates (user-approved):** build → baseline runs → treatment runs →
skill improvement → guarded self-improvement loop.

## Layout

- `SKILL.md` — current skill version (the artifact under test)
- `backups/SKILL.vN.md` — immutable version backups; rollback source
- `CHANGELOG.md` — what changed per version and why
- `evals/rubric.md` — scoring rules + scorecard template
- `evals/results/` — one scorecard per run (`<task>-<arm>-<n>.md`)
- `evals/tasks/` — 6 tasks in 3 tiers, each self-contained
  - `e1-log-triage` — file output from a log; runtime-free
  - `e2-csv-stats` — JSON stats from CSV; runtime-free
  - `m1-brackets` — Python function, hidden test battery
  - `m2-cart-bugs` — Python module with 3 seeded bugs; hidden battery
  - `h1-ttl-cache` — Python LRU+TTL cache; correctness + performance
  - `h2-grid-transform` — infer transformation rule from examples (ARC-style)
- `checkers/` — objective scorers (f). Agents under test MUST NOT read these.
- `tools/` — deterministic input generators

## Experiment protocol

1. **Arms.** Each task is run twice with a fresh `general` sub-agent:
   - `control`: task README only ("work autonomously").
   - `treatment`: task README + full SKILL.md injected + "follow this process".
   Identical model, identical task folder.
2. **Isolation.** The sub-agent is told to work only inside its assigned task
   folder and never read `avo-lab/checkers/`, `avo-lab/evals/results/`,
   `SKILL.md`, or other task folders (treatment gets SKILL.md contents inline
   precisely so it doesn't browse the lab).
3. **Scoring.** Run the task checker; paste verbatim output into a scorecard
   (template in rubric.md). Record: final SCORE, pass/fail, candidate count
   (from `avo/LINEAGE.md` if present), process violations observed.
4. **Comparison decision rule** (see rubric.md): skill "helps" only if
   treatment ≥ control on score AND shows fewer repeat-failure patterns.

## Anti-rogue policy (for later self-improvement stages)

- Improver agents may edit ONLY `SKILL.md` and `CHANGELOG.md`.
- Every proposed change must cite eval evidence (scorecard paths).
- `backups/` is append-only; any edit there voids the generation.
- A generation that fails to beat the previous version on the eval subset is
  rolled back from backup.
