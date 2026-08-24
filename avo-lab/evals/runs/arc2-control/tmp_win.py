rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
top,left=40,34
def w(t,l): return [rows[y][l:l+5] for y in range(t,t+5)]
for name,(t,l) in {"UP":(top-5,left),"DOWN":(top+5,left),"LEFT":(top,left-5),"RIGHT":(top,left+5)}.items():
    cells=["".join(r) for r in w(max(0,min(t,59)),max(0,min(l,59)))]
    print(name, cells, "has3=", any("3" in c for c in cells))
print("CUR:", ["".join(r) for r in w(top,left)])
