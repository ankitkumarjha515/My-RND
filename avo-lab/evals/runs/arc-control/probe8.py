import analyze as A
g, meta = A.load('t99.txt')
a = A.assembly(g)
A.PASS = set('3b01')
dist = A.bfs(g, a)
goal = (45,49)
pl = A.path(dist, goal)
seq=[a]; r,c=a
for s in pl:
    dr,dc={'1':(-5,0),'2':(5,0),'3':(0,-5),'4':(0,5)}[s]
    r,c=r+dr,c+dc; seq.append((r,c))
open('route2.txt','w').write(pl)
open('route2_nodes.txt','w').write(';'.join('%d,%d'%p for p in seq))
print(pl); print(seq)
