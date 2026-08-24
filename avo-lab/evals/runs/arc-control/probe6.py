import analyze as A
g, meta = A.load('t99.txt')
a = A.assembly(g)
print('start:', a)
A.PASS = set('3b01')   # allow standing over glyph cells for hypothetical dips
dist = A.bfs(g, a)
items = []
for p in sorted(dist.keys()):
    pl = A.path(dist, p)
    items.append((len(pl), p, pl))
items.sort()
print('--- all reachable by cost ---')
for L,p,pl in items:
    print(L, p, pl)
