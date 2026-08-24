import analyze as A
A.PASS = set('3b01')
g, meta = A.load('t80_down.txt')
a = A.assembly(g)
dist = A.bfs(g, a)
goal = (45,49)
seq = [a]
cur = a
path_ = A.path(dist, goal)
r, c = a
for sym in path_:
    dr, dc = {'1': (-5,0), '2': (5,0), '3': (0,-5), '4': (0,5)}[sym]
    r, c = r+dr, c+dc
    seq.append((r,c))
print(path_)
print(';'.join('%d,%d' % p for p in seq))
open('route1.txt','w').write(path_)
open('route1_nodes.txt','w').write(';'.join('%d,%d' % p for p in seq))
