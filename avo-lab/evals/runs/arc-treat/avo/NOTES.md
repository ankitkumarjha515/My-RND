# Mechanics Knowledge Base
(verified facts only; guesses marked UNVERIFIED)

## ⚠️ RUN TERMINAL (S3): GAME_OVER at step=143, levels 0/0, no grid. Server dead for this run.
- CAUSE: second meter-exhaustion death this session did NOT soft-respawn. Death#1 (step 119-121, sea lane) respawned normally at west passage w/ fresh 40. Death#2 (step 141-143, far-east c54-58) -> flood frame -> GAME_OVER.
- BEST MODEL: finite LIVES, cumulative across sessions (L1 flood + S2 flood + these two ≈ budget spent). Treat METER AS LIFE. Never plan chains that end in death.
- If a future session resumes: check whether reset restores lives or it is truly over.

## CORE RULES (L1+L2 verified)
- Grid 64x64 hex. Block = 5x5 (2 rows 'c' atop 3 rows '9'). A1=UP5 A2=DOWN5 A3=LEFT5 A4=RIGHT5. Moves are 5-cell JUMPS; blocked move = no move, still costs step + meter.
- TERRAIN: '4'=SOLID WALL. Walkable floor: '3','5' (+entities 0/1 sprite, b meter strip, 8 sockets). Box border rings are WALKABLE '3'; zigzag '9' cells are the actual lock blockers.
- METER: b-strip (rows 61-62) decays EXACTLY -2 per ACTION on L2 — **REFINED (S3)**: decays on SUCCESSFUL moves only; BLOCKED moves (walls/zigzag/mouth-bumps) cost step but ZERO meter (9 consecutive bumps: b-run byte-identical). len/2 = actions remaining. At len 0: that action still resolves; NEXT action renders all-b flood frame; NEXT action respawns you.
- FLOOD/DEATH (L2 verified): respawn at r40-44 c29-33 (west passage), meter refilled to 40 (c15-54), GLYPH RESET (variant C lost -> solid-top variant, presumed ORIG). levels kept.
- STATUS is FREE (no step cost): `driver.py client STATUS`. Actions: `driver.py client ACT ACTIONn`.
- NO b-diamonds on L2 upper map — **REFUTED (S3)**: diamond cluster existed r16-18 c15-17 (above box-2 shaft), eaten on descent, meter jumped ~18->~46 (+28ish). SECOND diamond visible r51-53 c49-51 (SE, below sprite). Diamond respawn rule UNKNOWN. Sockets c55-63 rows 61-62 show 588588588 when restored.

## L2 MAP (verified this session)
- Sea rows 10-14 continuous floor c9-53 (only full-width crossing lane); islands/walls at c24-28 + c39-43 rows 15-24, c39-48 rows 20-24, pocket c48-57 rows 20-24.
- East lane c44-58 floor rows 39-49 (sprite embedded at rows 46-48 c50-52, plus-shape center (47,51)); east shaft c49-53 rows 25-38; connects pocket->bottom field WITHOUT touching sprite if block stays at c44-48 until row <=44... (c44-48 clear of sprite cells).
- West passages: c34-43 rows 25-34 and c29-38 rows 35-44 (south DEAD END at row 45); link sea<->nothing useful.
- BOX-2: border ring r38/r46/c12/c19 walkable '3'; interior r39-45 c13-18 floor '5'; ZIGZAG LOCK: r41 c15-17, r42 c15, r43 c15+c17. Entry only via top shaft c14-18 rows 25-37; push DOWN lands block straddling r38/39 = entry moment.
- SPRITE EAT cost math from spawn: R,Ux6,Rx3,Dx7 = 17 acts (34 meter) to first eat; each extra eat = U,D cycle (2 acts). Mirror involution (eat twice = back to C) UNVERIFIED.

## HANDOFF STATE (end of session, step=80)
Block r20-24 c34-38 in sea, meter 30 (15 acts), glyph = post-flood variant (NOT C), levels 1/7.
NEXT EXPERIMENT (decisive, 11 acts, fits): keyless push-test U,U,Lx4,Dx5 -> push lands straddling box-2 border. If zigzag clears => C NOT needed on L2. If not => need sprite rotations but single-life chain impossible from spawn (short >=16) => hunt other mechanic (sockets? intended multi-life loop?).

## SESSION-3 RESULTS (step 80-93)
- Exp13 REFUTED: keyless push onto zigzag BLOCKED (block held straddling r38/39). Key REQUIRED.
- Mouth-bump flip reproduced on L2: BL floor 5->0 one-time; repeat bumps inert (Exp14 refuted).
- Zigzag exact cells: r40 c15-17, r41 c15, r42 c15+c17. Diamond#1 r16-18 c15-17 EATEN (+~28 meter).
- Box-2 lock math: sprite round-trip from mouth = 22 acts > any affordable budget; single-life chain from spawn = 17(eat)+1(diamond)+15+ return > 20 max. Impossibility PENDING better data (rotation count to C unknown; diamond respawn unknown).
- Plan: die at mouth (free - glyph already ORIG), respawn 40 meter, run spawn->sprite-eat->SE-diamond chain, OBSERVE rotation delta + diamond refill. Then decide final life.

## SESSION-3 LATE FINDINGS (steps 93-143, run ended)
- BLOCKED MOVES: cost step, ZERO meter (9 mouth bumps byte-identical). Also REDIRECT anomaly re-confirmed: blocked D on east descent landed block 5 cols RIGHT (c49-53 -> c54-58) — routes through unverified columns are UNRELIABLE.
- BL-room floor flip = PROXIMITY INDICATOR (not latch): 5->0 while resident at box-2 mouth, reverted 0->5 after leaving up the shaft (mirrors L1 sprite-ring behavior).
- GLYPH ROTATION confirmed on L2: one full east-passage descent rotated ORIG (full-row top) -> vertical-mirror variant (full row bottom). Rotation delta per pass = 1 step, direction = vertical mirror. Trigger (overlap vs proximity vs passage) UNRESOLVED — block never verifiably overlapped sprite cells; sprite visual intact after; diamond uneaten when footprint missed by 1+ cols.
- DIAMONDS only refill on actual footprint overlap (+~28 observed once). SE diamond r51-53 c49-51 still UNCLAIMED at run end.
- Sockets changed 588588533 -> 588533533 across first S3 death (meaning unknown).
- BOX-2 SOLUTION REQUIREMENT (updated): need glyph rotated from ORIG to whatever variant clears r40 c15-17/r41 c15/r42 c15+c17. Rotation passes available per life are LIMITED by meter-as-life math: spawn->east passage = ~13 acts minimum round trip; each pass rotates +1. If C = k rotations away, chain ≈ 13k + entry push. Feasible for small k IF no redirect surprises and NO death needed. This was the road not finished.

## Events log (correlations) — L1 legacy, superseded where noted
- Box-mouth visit (block r15-19 c34-38): BL room flipped 5->0 ONE-TIME (repeat bump: nothing).
- Sprite touch (block over r31-33 c20-22): sprite eaten; TOP BOX interior ring turned 5->0; BL room floor 0->5 AND its 9-shape MIRRORED horizontally.
- Moving up off sprite: box ring reverted 0->5.
- [SUPERSEDED by CORE RULES] old b-strip decay readings.
- Anomaly: early A3 up-shift + step+2 (unexplained).

## LEVEL 1 SOLVED (prior session): sprite-zone rotations set BL glyph; variant C = key; zigzag cleared on push-entry.
## LEVEL 2 findings
- Resumed mid-level at step=52 levels=1/7 with glyph=C intact (server persists across sessions despite "reset" briefings).
- Full mechanics + map + handoff in sections above. Zigzag lock NOT yet tested without key.
