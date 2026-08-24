import analyze as A
A.PASS = set('3b01')
g, meta = A.load('t80_down.txt')
a = A.assembly(g)
dist = A.bfs(g, a)
def cov(r,c,r0,r1,c0,c1):
    return any(r0<=r+dr<=r1 and c0<=c+dc<=c1 for dr in range(5) for dc in range(5))
digpos = [p for p in sorted(dist.keys()) if cov(p[0],p[1],46,48,50,52)]
print('digit-covering positions (if 1 passable):')
for p in digpos:
    print(' ', p, A.path(dist,p))
