rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
print("     "+"".join(str(x//10) for x in range(0,32)))
print("     "+"".join(str(x%10) for x in range(0,32)))
for y in range(40,64):
    print(f"{y:2d}   "+rows[y][0:32])
