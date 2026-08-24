from collections import deque
rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
def legal(t,l):
    if t<0 or l<0 or t>59 or l>59: return False
    win=[rows[y][x] for y in range(t,t+5) for x in range(l,l+5)]
    return any(c!="4" for c in win)
def locked(t,l):
    return not (t+4<39 or t>45 or l+4<13 or l>19)
moves={"U":(-5,0),"D":(5,0),"L":(0,-5),"R":(0,5)}
def bfs(start):
    prev={start:None}; q=deque([start])
    while q:
        cur=q.popleft()
        for k,(dt,dl) in moves.items():
            nxt=(cur[0]+dt,cur[1]+dl)
            if nxt not in prev and legal(*nxt) and not locked(*nxt):
                prev[nxt]=(cur,k); q.append(nxt)
    return prev
def path(prev,g):
    if g not in prev: return None
    p=[];cur=g
    while prev[cur]: p.append(prev[cur][1]); cur=prev[cur][0]
    return list(reversed(p))
p1=bfs((35,14))
print("from knock-spot:")
for g in [(15,14),(20,14)]:
    pp=path(p1,g); print(" ",g,len(pp) if pp else None,pp)
p2=bfs((15,14))
print("from diamond-A:")
for g in [(50,4),(55,4),(50,9)]:
    pp=path(p2,g); print(" ",g,len(pp) if pp else None,pp)
