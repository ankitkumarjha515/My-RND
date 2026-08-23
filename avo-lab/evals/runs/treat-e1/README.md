# E1 — Log triage (easy)

## Input
`app.log` in this folder. Line format (space-separated):

```
<ISO-8601-UTC-timestamp> <LEVEL> <message...>
```

Example: `2026-08-21T08:00:14Z ERROR auth failed user=33`

- The LEVEL is always the second space-separated token.
- Timestamps are zero-padded ISO strings; lexicographic order == chronological order.

## Task
Create `errors.txt` in this folder containing exactly the lines whose LEVEL
token is `ERROR`, sorted by timestamp ascending. Rules:

- Sort must be stable: lines with equal timestamps keep their original
  relative order from app.log.
- Copy lines verbatim — no reformatting, no trimming.
- File ends with a single trailing newline.

## Verification (f)
From the repo root:

```
python "avo-lab/checkers/e1_checker.py" "avo-lab/evals/tasks/e1-log-triage"
```

PASS requires 100/100. Beware decoy lines whose message text contains the
token ERROR but whose LEVEL is not ERROR.
