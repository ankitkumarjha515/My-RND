import sys
fn = sys.argv[1] if len(sys.argv) > 1 else "avo/cur.txt"
lines = [l.rstrip("\n") for l in open(fn) if len(l.rstrip("\n")) == 64 and set(l.strip()) <= set("0123456789cb")]
g = lines[:64]
def cell(r, c): return g[r][c]
# block bbox
rows = [i for i in range(64) for _ in range(1) if 'c' in g[i]]
crows = [i for i, l in enumerate(g) if 'c' in l]
nines_block = []
block_cells = [(i, j) for i in range(64) for j in range(64) if g[i][j] in 'c']
if block_cells:
    rs = sorted(set(r for r, c in block_cells)); cs = sorted(set(c for r, c in block_cells))
    # extend down for 9s under c
    print("BLOCK c-rows", rs[0], "-", rs[-1], "cols", cs[0], "-", cs[-1])
    r0, c0 = rs[0], cs[0]
    rr = r0
    while rr + 1 < 64 and g[rr + 1][c0] == '9':
        rr += 1
    print("BLOCK full bbox rows", r0, "-", rr, "cols", cs[0], "-", cs[-1])
# sprite zone: any of 0/1 not in expected floor areas -> print all 0/1 cells
z = [(i, j) for i in range(64) for j in range(64) if g[i][j] in '01']
print("ZERO/ONE cells:", z)
# b strip extent on its row
for i in range(64):
    if 'b' in g[i]:
        bs = [j for j in range(64) if g[i][j] == 'b']
        print(f"b-strip row {i}: cols {min(bs)}-{max(bs)} count={len(bs)}")
        break
# BL glyph: 9-cells in region rows>=52 cols<=12
gl = [(i, j) for i in range(52, 64) for j in range(0, 13) if g[i][j] == '9']
print("BL glyph 9-cells:", gl)
# sockets row
for i in range(60, 64):
    seg = [g[i][j] for j in range(52, 64)]
    print(f"sockets row {i}: {''.join(seg)}")
