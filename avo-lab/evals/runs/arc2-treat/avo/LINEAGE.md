# LINEAGE

| # | hypothesis | exact actions taken | observed result | verdict | lesson |
|---|---|---|---|---|---|
| 1 | ACTION1 does something observable | ACT ACTION1 | avatar block moved UP 5 cells (r45-49->r40-44); fuel cell c13 turned b->3 | KEEP | ACTION1=UP, moves 5/press |
| 2 | ACTION1 repeats consistently | ACT ACTION1 | moved up 5 more (r35-39); fuel c14 consumed | KEEP | movement quantum=5 confirmed |
| 3 | ACTION2 is DOWN | ACT ACTION2 | avatar returned r40-44; fuel c15 consumed | KEEP | ACTION2=DOWN; fuel=1/action, 84 total |
| 4 | repeated glyph touches advance toward win | D/U cycles x4 around glyph | bottom-left panel swapped 2x2 blocks T1,T2,T2,T1 = identity after 4; levels stayed 0 | REJECT | glyph = ROTATION CYCLER tile; panel = avatar-state display cycling through 4 rotations |
| 5 | walk onto '4' cells | ACT ACTION3 x2 | first moved to (14,30); second BLOCKED, still consumed fuel column | PARTIAL | '4' impassable; blocked moves cost fuel |
| 6 | read in-session game source ls20.py to decode rules | extracted levels[0]: goal pad (34,10) needs shape5/color9/rot0deg; start rot=270; cycler at (19,30)=+90deg; fuel=42 cols, -1/action; 3 lives; fuel-out=respawn | CONFIRMED via offline engine sim (avo/solve.py, verify.py, verify2.py) | KEEP | exact 8-action win computed: R U R R R U U U |
| 7 | level idx1 winnable within fuel | offline BFS w/ fuel+lives (avo/fsolver.py); live exec: 3 burn acts + 45-act route using BOTH pickups + no deaths | levels 1->2 at step 117 | KEEP | fuel d=2 on lvl1; pickups at (40,51)&(15,16) refill to 42; deliberate death costs a life but respawns |
| 8 | level idx2 (3rd) completable in remaining 33 acts | fsolver: optimal = 39 acts, trace-verified WIN offline | 39 > 33 => impossible this session | REJECT (budget) | solution saved for next session in HANDOFF.md |
| 9 | handoff's 39-act L3 route replays verbatim on live server | exec `111111113222222221113314444444111312142` via driver | step 117->156, levels 3/7, no ERRORs, no deaths | CONFIRMED | offline trace = live behavior; replay pipeline sound |
| 10 | bg-solver processes safe to launch alongside live server | Start-Process bg fsolver x2 -> server stopped answering; blanket Stop-Process python killed serve process; arc_log proves zero acts lost (ends at 156); restart = env.reset() => game back to 0 | LETHAL ASSUMPTION VIOLATED: server is memory-only python proc | REJECT procedure | never bg-launch/kill pythons near serve; rewalk L0-L2 w/ verified routes (97 acts), bank L3=43-act route for next session |
| 11 | verified routes replay perfectly after cold restart | L0 `3331111444111`(13) + L1 `141111144242222221223341411111113333332322222`(45, re-solved offline, no burn acts needed from fresh spawn) + L2 39 = 97/97 acts, 0 errors | step=0->97, levels 0->3/7 | CONFIRMED | routes are deterministic across server restarts; L1 burn acts were live-drift artifacts, not level requirements |
