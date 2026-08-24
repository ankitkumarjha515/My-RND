# ls20 — mechanics learned (session 2)

## Core rules (verified empirically)
- A1/A2/A3/A4 = UP/DOWN/LEFT/RIGHT for the bomb-block (cccc=fuse rows on top, 99999 body below; 5x5 footprint).
- Movement strides are exactly 5 cells; landing lattice: top row index ≡ 0 (mod 5), left col ≡ 4 (mod 5) from standard spawns. First-ever move may snap -6 (L1 start 46→40).
- Map is INVERTED painting: '3' = walkable corridor/wall-structure you may occupy; '4' = solid VOID (never landable); '5' rooms / '9' clusters / 'b' diamonds are special.
- A move is legal iff its 5x5 destination window contains at least one non-'4' cell — EXCEPT room interiors ('5') which need unlock state (see below). Locked-room-adjacent windows can also refuse.
- Fuse strip (rows 61-62, 'b' cells) burns ~4 cells/action (successful AND some stuck moves); when it hits 0, the NEXT action triggers a FLASH: lose one '88'-pair life, fuse resets to ~96, block teleports to ~(rows40-44, cols29-33), avatar respawns, outlines clear.
- Diamonds ('bbb/b3b/bbb'): covering one with the block PAUSES the burn and REGENS fuse (+~32) — ONE TIME ONLY per diamond per flash-cycle. Uncovering resumes the burn.
- Avatar sprite (0/1 cells): crushing it (block fully over it) on L1 unlocked target-room entry + outlined rooms. On L2 crush alone did NOT unlock; instead KNOCKING a locked room door (press toward it; move sticks, costs nothing) outlines the NEXT TARGET room.
- L2 win path (incomplete): knock west room door at (35,14)->D highlights SW room -> enter SW cluster room. BUT SW room is geographically sealed behind the locked west-room window (40,14); needs either a second knock-target cycle or a route unknown. West cluster window = (40,14); SW cluster window = (55,4) (covers rows55-59 of cluster; row60 cells unreachable on lattice).

## Level 1 optimal route (~15 moves, verified)
Start (46,34): U (snaps to 40) ; U,U,U -> band rows25-29 ; L,L,L -> (25,19) ; D -> CRUSH avatar at (30,19) ; R,R,R -> (25,34) ; U,U,U,U -> rows10-14 = WIN (cover target cluster).
Caveat: exact void layout varies per world seed; verify with BFS (tmp_bfs*.py pattern in grids/cur.txt).

## Infrastructure warnings
- driver.py servers DIE silently (also when an agent shell call times out — process tree kill). If STATUS returns stale/GAME_OVER or client times out: check Win32_Process for `driver.py serve`, kill strays, restart same game id, count actions HONESTLY across restarts.
- First env.step after serve can take >90s (client timeout) — write cmd.txt directly and poll resp.txt manually instead of using `driver.py client`.
