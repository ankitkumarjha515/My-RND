# NOTES — verified facts only (guesses marked UNVERIFIED)

- README spec: `errors.txt` = lines whose 2nd space-separated token == `ERROR`, stable-sorted by timestamp (token 1), verbatim copy, single trailing newline.
- Decoy lines exist: message text contains literal token `ERROR` but LEVEL is WARN/INFO (app.log lines 57, 59, 67, 101, 130, 136, 137). Must match token position 2 only.
- app.log has 142 lines; timestamps lexicographic == chronological. Line 101 is an out-of-order INFO line (timestamp 08:00:00Z appears late in file) — proves sort must actually reorder, but that line is INFO so it does not affect ERROR set ordering. UNVERIFIED whether any ERROR lines are out of order — apply stable sort regardless.
- Checker groups observed: file-exists, line-set, exact-match. PASS needs 100/100.
- VERIFIED: 31 ERROR lines in app.log; errors.txt written as UTF-8 bytes, one line + `\n` each → checker PASS 100/100 (candidate #1 COMMIT). No ERROR lines were out of chronological order, but stable sort applied anyway.
