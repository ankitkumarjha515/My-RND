import glob
def loadmeta(p):
    rows=[];step=None
    for l in open(p):
        l=l.strip()
        if len(l)==64 and all(c in "0123456789abcdefABC" for c in l): rows.append(l)
        elif l.startswith("step="): step=l
    return rows,step
for f in sorted(glob.glob("grids/s5*.txt")):
    rows,st=loadmeta(f)
    if not rows: continue
    zeros=sum(r.count("0") for r in rows)
    ones=sum(r.count("1") for r in rows)
    if zeros>6 or ones>0:
        print(f,st,"zeros=",zeros,"ones=",ones)
