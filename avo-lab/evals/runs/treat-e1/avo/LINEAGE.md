# LINEAGE — append-only candidate ledger

| # | hypothesis | change made | eval cmd + real result | verdict | lesson |
|---|------------|-------------|------------------------|---------|--------|
| 0 | Baseline: task not yet done; f should FAIL | none (untouched start) | `python "avo-lab\checkers\e1_checker.py" "avo-lab\evals\runs\treat-e1"` → `FAIL file-exists: errors.txt missing` / `FAIL line-set:` / `FAIL exact-match:` / `SCORE 0/100 FAIL` | REJECT (baseline) | errors.txt must exist; three check groups: file-exists, line-set, exact-match |
| 1 | Lines with `line.split(' ',2)[1] == 'ERROR'`, stable sort by token 0, verbatim bytes + `\n` each → passes all groups | Created errors.txt (31 lines) via inline Python reading app.log as bytes | same cmd → `OK file-exists: 31 lines` / `OK line-set: expected 31 error lines, got 31 lines` / `OK exact-match: verbatim content, stable order, single trailing newline` / `SCORE 100/100 PASS` | COMMIT | Decoys avoided by matching LEVEL at token index 1 only; byte-level write preserves verbatim content |
