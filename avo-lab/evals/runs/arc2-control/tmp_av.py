def find(p):
    rows=[l.strip() for l in open(p) if len(l.strip())==64]
    cells=[(y,x,rows[y][x]) for y in range(64) for x in range(64) if rows[y][x] in "01"]
    print(p, sorted(cells))
find("grids/s115_ACTION1.txt")
find("grids/cur.txt")
