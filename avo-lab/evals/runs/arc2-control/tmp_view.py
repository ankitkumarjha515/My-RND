import sys
rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
for y in range(5,52):
    print(f"{y:2d} "+"".join(rows[y][x] if x%5 else rows[y][x].upper() for x in range(9,59)))
