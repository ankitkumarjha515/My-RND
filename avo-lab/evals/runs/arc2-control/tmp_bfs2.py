from collections import deque
rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
def legal(t,l):
    if t<0 or l<0 or t>59 or l>59: return False
    win=[rows[y][x] for y in range(t,t+5) for x in range(l,l+5)]
    return any(c!="4" for c in win)
# find block, diamonds, avatar
for y,r in enumerate(rows):
    if "c" in r: print("block c-row:",y,"cols",[x for x in range(64) if r[x]=="c"]); break
bs=[(y,x) for y in range(64) for x in range(64) if rows[y][x] in "bB"]
print("diamond cells:", sorted(set(bs)))
avs=[(y,x) for y in range(64) for x in range(64) if rows[y][x] in "01"]
print("avatar cells:", avs)
start=(35,29)
moves={"U":(-5,0),"D":(5,0),"L":(0,-5),"R":(0,5)}
prev={start:None}; q=deque([start])
while q:
    cur=q.popleft()
    for k,(dt,dl) in moves.items():
        nxt=(cur[0]+dt,cur[1]+dl)
        if nxt not in prev and legal(*nxt):
            prev[nxt]=(cur,k); q.append(nxt)
def path(g):
    if g not in prev: return None
    p=[];cur=g
    while prev[cur]: p.append(prev[cur][1]); cur=prev[cur][0]
    return list(reversed(p))
# goals: windows covering each diamond cluster
ds=sorted(set(bs))
if ds:
    ys=[y for y,x in ds]; xs=[x for y,x in ds]
    print("diamond bbox rows",min(ys),max(ys),"cols",min(xs),max(xs))
    for name,g in {"A?":(15,14),"B?":(50,39)}.items():
        p=path(g); print(name,g,"->",p)
