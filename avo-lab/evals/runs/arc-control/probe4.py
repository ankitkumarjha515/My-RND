import analyze as A
g, meta = A.load('t80_down.txt')
for r,c in [(10,14),(15,49),(45,49)]:
    print((r,c), [g.get((r+dr,c+dc),'?') for dr in range(5) for dc in range(5)].count('4'), 'walls in box')
print('row10:', ''.join(g.get((10,c),'?') for c in range(0,65)))
