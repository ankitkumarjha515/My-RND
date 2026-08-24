# HANDOFF — arc2-treat (game ls20-9607627b) — written END of session 2

## Current state (server RUNNING, do NOT restart unless dead)
- Server: ONE pair — venv shim PID 13120 -> anaconda python PID 8644, cmdline `driver.py serve ls20-9607627b`.
- Live: step=97, levels=3/7, avatar at FRESH level-index-3 spawn, fuel 42/42, lives 3.
- Session-2 budget used: 136/150 accepted actions (39 on first L3 win + 97 on post-crash rewalk). Next session gets its own fresh 150.

## ⚠️ INCIDENT (read before doing anything)
Session 2 killed the server twice:
1. Launching bg solver processes from the agent shell froze/killed the serve process
   (console teardown). THEN a blanket `Get-Process python | Stop-Process` finished the job.
   Server state is MEMORY-ONLY => restart = env.reset() = game back to step 0.
   Recovery cost: 97 acts to rewalk L0-L2. DO NOT REPEAT.
2. RULES: run all solvers FOREGROUND. Never `Stop-Process` without listing PIDs first.
   venv python.exe is a shim that spawns an anaconda child (same cmdline) — one launch
   looks like TWO processes; count PAIRS. After ANY server start, verify exactly one pair.

## NEXT DECISIVE EXPERIMENT (exact sequence)
Level index 3 (4th level), verified TWO ways today (offline vwin + live exec):
`3332223223312121211331233111224111141411333`  (1=U,2=D,3=L,4=R; 43 acts)
Executed from current state it wins at act 43 -> levels 4/7, fuel 42, lives 3.
Then budget ~107 remains for idx 4,5,6. Solve each offline FIRST:
  python avo\fsolver.py <i>      (foreground! expect minutes; ignore buggy "replay won" line)
  python avo\vwin.py <i> <SEQ1>  (correct verifier: prints WIN at act N or NO WIN/DIE)
Estimated costs by baseline ratio (~0.55x of human_baseline [84,96,186]): L4~45, L5~50,
L6(fog)>100 — likely only L4+L5 fit; if so stop at fresh idx6 spawn and hand off again.

## Mechanics additions this session (all in NOTES.md "Session 2 additions")
- fsolver.py now snapshots wanderers (levels idx>=4 may have xfmluydglp regions;
  they step pre-move each ACT and UNDO when avatar is wall-blocked).
- Platform rides complete within a single ACT => between-action BFS state stays sound.
- vwin.py = trustworthy replay verifier.

## Files
- avo/LINEAGE.md rows 1-11, avo/NOTES.md (facts + server ops law),
  avo/fsolver.py (extended), avo/vwin.py (verifier), sol3.txt (L3 solution proven),
  s0*.txt frames (s0069.txt = full old level-1 map view).
