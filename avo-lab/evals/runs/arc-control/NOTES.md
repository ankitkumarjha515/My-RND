# ARC game notes (mechanics reverse-engineered)

## Actions
- ACTION1=up, ACTION2=down, ACTION3=left, ACTION4=right. Assembly moves 5 cells/press.
- driver.py client STATUS = free; ACT consumes step budget. Save every response frame!

## LEVEL 1 — SOLVED (win confirmed at q66.txt, step 66)
- Win = ride assembly INTO an entry-slot. NO source-pattern editing needed.
- Sequence: shaft col34-38 up 36->16 (5x A1), A1 again = BLOCKED at 16 (pre-unlock),
  go down/left, DIP down at (26,c19)->(31,c19): FREE move, flips switch glyph
  ('1' appears at row34,col21 inside landing box), return to shaft, now A1 passes
  16->11 INTO slot at rows 11-15 => level complete on that press.
- Energy L1: -1 per successful move, blocked/dip = free. Bar ~40.

## LEVEL 2 — mechanics decoded in session 3 (episode died at step 121, GAME_OVER)
- ENERGY IS THE CORE CONSTRAINT: -2 per successful move. Blocked presses cost 0
  (verified at delivery pocket) but start-pocket blocked presses drained -2 in old
  session (unverified anomaly). Full bar ~36-40 => ~18 moves per life.
- Bar hits 0 + any action => first time: all-'b' FLASH then SOFT RESET (respawn at
  start pocket rows41-45/c29-33, bar refilled, rings restored, source resealed).
  SECOND energy death => GameState.GAME_OVER, levels=0/0, EPISODE TERMINAL.
  (Unclear if lives>2 exist; do not test casually.)
- START POCKET: only RIGHT open ((40,29)->(40,34)); up/left/down walled.
- MAP connectivity (BFS-verified, passable = not-'4'): from start you can reach the
  whole top band (rows 5-20), col49 shaft down to (50,x), bottom-right hall,
  delivery pocket via top: route start->pocket(35,14) = '1411111333223222' (16),
  start->DIGIT PAD (45,49) = '14111114424222222' (17, last press is the dip itself).
- RINGS dissolve when assembly overlaps them (ring1 rows17-19/c15-17 sits ON the
  pocket route; ring2 rows51-53/c40-42). No visible effect; restored on reset.
- DIGIT PAD (the edit mechanism!): glyph cluster rows46-48/cols50-52 ('0'/'1' cells).
  Landing the assembly box on it (via DOWN from (40,49)) REMOTELY EDITS the source
  room bands. Each dip transforms:
    dip1: band1 FULL<->pairs SWAP with band3 (b1: FULL->pairs, b3: pairs->FULL)
    dip2: band2 RIGHT-pair -> LEFT-pair
  (cycle order beyond dip2 unknown - episode died)
- SOURCE room bottom-left rows54-61/cols1-10, bands 6-wide at cols3-8.
  Fresh state [FULL / RIGHT-pair / LEFT+RIGHT pairs].
  After dip1+dip2: [pairs(3-4,7-8) / LEFT-pair(3-4) / FULL].
- TARGET display room rows40-46/c13-21 wants [mid-triple / left / left+right]
  (9-cells at rows41/42/43 = cols16-18 / 16 / 16+18).
- DELIVERY: pocket above target room, cargo-top (35,14) (sealed left/right, UP open
  to top band, DOWN = into slot). DOWN was BLOCKED pre-edit (free no-op). NOT yet
  tested after edits - THE key next experiment.
- UNKNOWN: do source-band edits PERSIST through soft reset? (rings/walls reset;
  bands untested). If they persist: multi-life plan = dip as much as possible per
  life, deliver in final life. If not: must solve dips+delivery in ONE 18-move life
  => likely need shorter routes or fewer required dips (find more pads?).
- '588588...' glyphs on bar rows = static decoration. Digit cluster may be a display
  of remaining transformations (was 010/100/1 pattern; hidden under assembly after).

## SESSION 3 LOG (steps 80-121)
- 80: A2 at delivery pocket = blocked, FREE (no drain).
- 81-97: grand tour to bottom-right; DISCOVERED -2/move drain (bar 34->0).
- 98-99: energy death #1 -> flash -> soft reset (rings back, walls sealed).
- 100-116: reroute to digit pad, DIP landed (edit #1: bands swap).
- 117-118: dip #2 (band2 right->left pair). Edits CONFIRMED cyclical.
- 119-120: retreat; energy death #2 => GAME_OVER. Episode over at step=121.
- Analysis tools built: analyze.py (grid parser/BFS/path), executor.py (verified
  route runner), probe*.py. Frames r10*/r2*/x1*.txt = this session.
