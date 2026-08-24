import analyze as A
g, meta = A.load('t80_down.txt')
a = A.assembly(g)
dist = A.bfs(g, a)
pos = sorted(dist.keys())
print('reachable:', pos)
def cov(r,c,r0,r1,c0,c1):
    return any(r0<=r+dr<=r1 and c0<=c+dc<=c1 for dr in range(5) for dc in range(5))
ringpos = [p for p in pos if cov(p[0],p[1],51,53,40,42)]
print('positions covering ring2:', ringpos)
digpos = [p for p in pos if cov(p[0],p[1],46,48,50,52)]
print('positions covering digit cluster:', digpos)
for p in ringpos[:6]:
    print('ring route', p, A.path(dist,p))
for p in digpos[:6]:
    print('digit route', p, A.path(dist,p))
