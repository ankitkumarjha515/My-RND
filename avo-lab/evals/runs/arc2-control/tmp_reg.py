rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
print("    "+"".join(str(x//10) for x in range(20,55)))
print("    "+"".join(str(x%10) for x in range(20,55)))
for y in range(38,58):
    print(f"{y:2d}  "+rows[y][20:55])
