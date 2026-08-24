rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
zs=sum(r.count("0") for r in rows)
os_=sum(r.count("1") for r in rows)
print("zeros:",zs,"ones:",os_)
av=[(y,x) for y in range(64) for x in range(64) if rows[y][x] in "01" and not (45<=y<=49)]
print("avatar cells:",[(y,x) for y,x in av])
# avatar region check rows46-48 cols50-52
print("avatar zone:",[rows[y][50] for y in range(46,49)])
