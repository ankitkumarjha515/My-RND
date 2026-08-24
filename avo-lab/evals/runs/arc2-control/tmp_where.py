rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
zs=[(y,x) for y in range(64) for x in range(64) if rows[y][x]=="0"]
ys=[y for y,x in zs]; xs=[x for y,x in zs]
print("outline bbox rows",min(ys),"-",max(ys)," cols",min(xs),"-",max(xs))
import collections
byrow=collections.Counter(y for y,x in zs)
print("rows with 0s:",dict(sorted(byrow.items())))
