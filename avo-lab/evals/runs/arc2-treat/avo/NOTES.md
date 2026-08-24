# NOTES (evidence-tagged)

## Ground [verified: driver.py read + frames]
- Game: ARC-AGI-3, grid 64w x 62h rendered as hex chars 0-f. step0 frame in ready.txt; free re-observe via `driver.py client STATUS` (does NOT increment steps).
- Levels: 0/7 done. human_baseline_actions_per_level=[22,123,73,84,96,192,186]. Budget: 150 actions max.
- available_actions = 1,2,3,4 only. No ACTION6.
- arc_log.jsonl logs per-step metadata (state, levels_completed).
- Permanence unknown yet; no lives/meters observed so far.

## Map features (step0, 0-indexed rc) [verified: diff.py]
- Avatar candidate A: 5x5 block cols34-38, top2 rows=c, bottom3 rows=9, initially rows45-49. ACTION1 moved it UP exactly 5 cells (to rows40-44).
- Room top-right: rows8-16 cols32-40, walls=3, interior=5 with some 9s inside (r11c35-37=999, r12c39?, r14c35..). 
- Small pattern rows31-33 cols17-20: 0/1 cells (like tiny arrow/dot).
- Structure rows40-49 cols34-38 area = avatar start region.
- Bottom-left: rows52-61 big 9/5 structures; row60-61: long 5-bar cols14-56ish, b-block cols15-53 (rows60-61), 88-pattern cols57-63.
- r61-62c13: initial b -> 3 after first ACTION1 (some indicator or door changed).

## Action semantics
- ACTION1 = UP move, 5 cells per press [verified: s000 vs s001 diff].

## Map (64x64, 0-indexed) [verified: look.py on s003]
- Hall: r25-51 x c14-52 floor=3; wall column c29-33 r30-39; avatar start r45-49 c34-38 (5x5: top2=c, bot3=9).
- Top-right room: walls r8/r16+c33/c41, interior 5s c34-40 r9-15; 9-glyph: (11,36..38),(12,38),(13,36),(13,38). Corridor r17-24 c35-37 (WIDTH 3 < avatar 5!).
- Glyph: (31,21)=0, (32,19)=1,(32,20)=0,(32,21)=0, (33,21)=1. Tiny vs 5-cell move quantum.
- Bottom-left: 9-blocks r55-60 c3-4/c7-8 etc; long 5-bar r60-63; 8-pair pattern r61-62 c56-63 (12 eights).
- Fuel bar: r61-62 c13-54, 84 b-cells, consumes 1 per action, b->3 from LEFT.
## Hypotheses pending
- H-fuel-death: fuel empty => death/reset [UNTESTED, expensive]
- H-goal: reach room / step on glyph / match 9-shape [UNTESTED]

## DECODED MECHANICS [verified: environment_files/ls20/9607627b/ls20.py + offline sim]
- Game ls20: avatar 5x5 moves by own size (ACTION1=U,2=D,3=L,4=R). Win level: step on ALL goal pads with avatar shape+color+rotation EXACTLY matching pad spec.
- Tiles: ihdgageizm=walls(pixel-perfect 5x5); ttfwljgohq/soyhouuebz/rhsxkxzdjz=cycler(shape/color/rotation +1 mod n); npxgalaybz=fuel refill pickup; rjlbuycveu=goal pad (wrong state => bump+5-frame flash, inputs swallowed, NO fuel cost); gbvqrjtaqo=moving platforms carrying avatar.
- Wrong-state goal contact blocks movement + flashes ~5 frames (no fuel).
- Fuel bar bottom: 42 columns, -1 per normal action; empty => lose 1 life (of 3, shown as 88 pips bottom-right), respawn at start with refuel.
- Bottom-left 10x10 box = current avatar form display. Top-right room = goal; small glyph inside = required form preview; ring flashes when a goal currently matches.
- LEVEL1 SOLVED (offline-verified): from spawn: LLL UUUU RRR UUU =13 acts; from (14,30) rot270: R U R R R U U U =8 acts -> level 2 at (29,40).

## Session 2 additions [verified: ls20.py read + live]
- L3 route PROVEN LIVE then re-proven after restart: `3332223223312121211331233111224111141411333` (43 acts, wins at act 43, fuel 42, lives 3; offline vwin + live exec #9).
- Wanderers (dboxixicic, xfmluydglp region): step ONCE per ACT before avatar moves; UNDO their step if avatar's move was wall-blocked. State = (x,y,dir,undo_x,undo_y,undo_dir); fsolver.py now snapshots them.
- Platforms (twkzhcfelv): push-slide only on avatar collision, 8 frames out / 6 back, ALL WITHIN ONE ACT (post-ACT they rest at start pos) => fsolver state without platforms is sound between actions. Direction = sprite-name suffix t/b/l/r.
- aqygnziho = per-level fuel action counter (-1 per normal act, 0 => lose() respawn+refuel+goal reset); _step_counter_ui is the visual bar. Wrong-pad contact still collects pads even at 0 fuel (edge case, untested).
- venv python.exe is a SHIM that spawns anaconda python child => every launch = 2 OS procs with SAME cmdline. Count pairs before killing!
- SERVER OPS LAW: serve holds game in MEMORY only. Any python kill or crash => env.reset(), step=0. Never Start-Process bg jobs from tool shells (console teardown froze/killed server once). Run solvers FOREGROUND only.
- avo/vwin.py <level_idx> <seq>: correct replay verifier (watches level_index change; fsolver's "replay won" line is buggy — ignore it).
- Levels idx4/5 unsolved yet (sol4/sol5.txt empty; bg attempt aborted). Level idx6 Fog=True render-only.
