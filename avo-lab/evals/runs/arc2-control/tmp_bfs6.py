from collections import deque
rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
def legal(t,l):
    if t<0 or l<0 or t>59 or l>59: return False
    win=[rows[y][x] for y in range(t,t+5) for x in range(l,l+5)]
    return any(c!="4" for c in win)
start=(40,29)
moves={"U":(-5,0),"D":(5,0),"L":(0,-5),"R":(0,5)}
prev={start:None}; q=deque([start])
while q:
    cur=q.popleft()
    for k,(dt,dl) in moves.items():
        nxt=(cur[0]+dt,cur[1]+dl)
        if nxt not in prev and legal(*nxt):
            prev[nxt]=(cur,k); q.append(nxt)
g=(40,14)
if g in prev:
    p=[];cur=g
    while prev[cur]: p.append(prev[cur][1]); cur=prev[cur][0]
    print(len(p),list(reversed(p)))
else: print("UNREACHABLE")
