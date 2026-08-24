import analyze as A
g, meta = A.load('t99.txt')
a = A.assembly(g)
print('assembly:', a)
# forbid the reset-trap node
orig = A.passable
def passable2(gg, r, c):
    if (r, c) == (40, 49):
        return False
    return orig(gg, r, c)
A.passable = passable2
dist = A.bfs(g, a)
pos = sorted(dist.keys())
print('reachable:', len(pos))
print(pos)
def cov(r,c,r0,r1,c0,c1):
    return any(r0<=r+dr<=r1 and c0<=c+dc<=c1 for dr in range(5) for dc in range(5))
for name,(r0,r1,c0,c1) in {'ring1':(17,19,15,17),'ring2':(51,53,40,43),'digits':(46,48,50,52)}.items():
    ps = [p for p in pos if cov(p[0],p[1],r0,r1,c0,c1)]
    print(name, '->', [(p, A.path(dist,p)) for p in ps[:4]])
# delivery pocket
ps = [p for p in pos if p == (35,14)]
print('pocket ->', [(p, A.path(dist,p)) for p in ps])
open('route_back.txt','w').write(A.path(dist,(35,14)))
