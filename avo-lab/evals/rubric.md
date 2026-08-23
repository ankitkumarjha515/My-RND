# Eval rubric

## Checker output contract

Every checker in `checkers/` prints one line per test group:

```
OK   <group>: <detail>
FAIL <group>: <detail>
```

then exactly one final line:

```
SCORE <points>/<100> PASS|FAIL
```

- `points` = passed test-group weight sum (partial credit preserved for lineage).
- PASS requires 100/100 for e1/e2/m1/m2/h2. h1 additionally enforces a
  performance group; failing it caps the score at 89 FAIL even if correctness
  is 100.

## Scorecard template (`evals/results/<task>-<arm>-<n>.md`)

```md
# <task> — <arm> run <n>
- Date: YYYY-MM-DD HH:MM
- Final SCORE: <paste checker final line verbatim>
- Full checker output: <paste>
- Candidates tried: <count from task avo/LINEAGE.md, or "no ledger">
- Process notes: <did the agent paste real outputs? repeat any rejected
  hypothesis? switch strategy after repeated failure? claim done without green f?>
- Verdict: pass | fail | partial
```

## Comparison decision rule (control vs treatment)

The skill HELPS on a tier if treatment shows:
1. Equal or higher SCORE on the tier's tasks, AND
2. Fewer process violations: resubmitting a rejected hypothesis unchanged,
   claiming done without executed-green evidence, or no diagnosis between
   failures.

If scores tie but process violations drop, record "process win" — expect score
effects to appear on harder tiers first (that is where search discipline pays).

Known confound to log honestly: sub-agents share the same base model as the
orchestrator; results measure process discipline effects, not model capability.
