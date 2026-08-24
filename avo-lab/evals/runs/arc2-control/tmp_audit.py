import glob,re
def load(p):
    return [l.strip() for l in open(p) if len(l.strip())==64 and all(c in "0123456789abcdefABC" for c in l.strip())]
def blk(rows):
    ts=[y for y,r in enumerate(rows) if "c" in r]
    if not ts or len(rows)<64: return None
    t=min(ts); xs=[x for y in range(t,min(t+5,64)) for x in range(64) if rows[y][x]=="c"]
    return (t,min(xs)) if xs else None
D={"ACTION1":(-5,0),"ACTION2":(5,0),"ACTION3":(0,-5),"ACTION4":(0,5)}
files=sorted(glob.glob("grids/s1*.txt"))
prev=None; pf=None
for f in files:
    m=re.search(r"s\d+_(ACTION\d)",f)
    if not m: continue
    act=m.group(1)
    rows=load(f); b=blk(rows)
    if prev and b:
        pt,pl=prev; t,l=b
        ed=D.get(act,(0,0))
        dt,dl=t-pt,l-pl
        verdict="MOVED" if (dt,dl)==ed else ("STUCK" if (dt,dl)==(0,0) else f"OTHER({dt},{dl})")
        it,il=pt+ed[0],pl+ed[1]
        prows=load(pf)
        def border(rr,t2,l2):
            if t2<0 or l2<0 or t2>59 or l2>59: return "OOB"
            top="".join(rr[t2][x] for x in range(l2,l2+5)); bot="".join(rr[t2+4][x] for x in range(l2,l2+5))
            lef="".join(rr[y][l2] for y in range(t2,t2+5)); rig="".join(rr[y][l2+4] for y in range(t2,t2+5))
            return top+"/"+bot+"/"+lef+"/"+rig
        print(f"{pf.split(chr(92))[-1][:4]}-{act}: {verdict} destborder={border(prows,it,il)}")
    if b: prev=b; pf=f
