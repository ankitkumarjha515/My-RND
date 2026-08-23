# NOTES — treat-h2

## Grounding
- Goal: infer the INPUT->OUTPUT rule from 4 examples in examples.txt; apply to inputs/h1,h2,h3; write outputs/h{n}_out.txt. Score = exact match x3 (~33 each), PASS at 100.
- NOT asked: nothing else; no explanation file required.
- Files: examples.txt, inputs/{h1,h2,h3}.txt (7-col grids; h1,h3 are 7x7, h2 is 7x7).

## Inferred rule (VERIFIED: checker SCORE 100/100 PASS on all 3 unseen grids, candidate #1)
A connected component of 0-cells (4-connectivity) is filled with color c iff:
1. it contains NO cell on the grid border, AND
2. every nonzero cell 4-adjacent to the component has the same value c.

Evidence per example:
- Ex1: interior of 3-frame surrounded purely by 3s -> filled with 3. Bottom zero band touches border -> unchanged.
- Ex2: interior of 7-frame filled with 7. The 5 diagonal line encloses no zeros -> unchanged (matches).
- Ex3: interiors of both the 2-ring and the 5-ring filled (each surrounded by its own single color). The 8 shape's zeros touch the bottom border / mixed colors -> unchanged.
- Ex4 (negative case): central 3x3 zero block is enclosed but by BOTH 4s and 9s (mixed surround) -> NOT modified. This is exactly why the "single color" condition exists.

Predictions:
- h1: fill rows1-3 cols1-5 region with 6; bottom band + lone 3 untouched.
- h2: fill (1,1)->1, (2,5)->4, (5,1)->2; col-3 corridor and (6,5) touch border -> unchanged.
- h3: only innermost (3,3) filled with 2; corridor between 1-frame and 2-ring has MIXED surround {1,2} -> unchanged (same mechanism as Ex4 negative case).

UNVERIFIED guesses: none material; 8-connectivity vs 4 makes no difference on these grids (checked by hand).
