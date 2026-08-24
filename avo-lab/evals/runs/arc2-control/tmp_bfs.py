from collections import deque
rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
def legal(t,l):
    if t<0 or l<0 or t>59 or l>59: return False
    win=[rows[y][x] for y in range(t,t+5) for x in range(l,l+5)]
    return any(c!="4" for c in win)
start=(40,34)
moves={"U":(-5,0,"ACTION1"),"D":(5,0,"ACTION2"),"L":(0,-5,"ACTION3"),"R":(0,5,"ACTION4")}
prev={start:None}; q=deque([start])
while q:
    cur=q.popleft()
    for k,(dt,dl,_) in moves.items():
        nxt=(cur[0]+dt,cur[1]+dl)
        if nxt not in prev and legal(*nxt):
            prev[nxt]=(cur,k); q.append(nxt)
goals={"diaB":(50,39),"avatar":(45,49),"diaA":(15,14)}
for name,g in goals.items():
    if g in prev:
        path=[]; cur=g
        while prev[cur]: path.append(prev[cur][1]); cur=prev[cur][0]
        print(f"{name}: REACHABLE {len(path)} moves: {list(reversed(path))}")
    else:
        print(f"{name}: UNREACHABLE")
print("total reachable:",len(prev))
