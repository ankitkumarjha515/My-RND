import analyze as A
g, meta = A.load('t99.txt')
a = A.assembly(g)
A.PASS = set('3b05901')
dist = A.bfs(g, a)
items = sorted((len(A.path(dist,p)), p, A.path(dist,p)) for p in dist)
print('reachable count:', len(items))
for L,p,pl in items[:40]:
    print(L, p, pl)
def cov(r,c,r0,r1,c0,c1):
    return any(r0<=r+dr<=r1 and c0<=c+dc<=c1 for dr in range(5) for dc in range(5))
print('--- targets ---')
for name,(r0,r1,c0,c1) in {'ring1':(17,19,15,17),'ring2':(51,53,40,43),'digits':(46,48,50,52),'slot-under-pocket':(38,39,14,18)}.items():
    ps = sorted((len(A.path(dist,p)),p,A.path(dist,p)) for p in dist if cov(p[0],p[1],r0,r1,c0,c1))
    print(name, ps[:3])
