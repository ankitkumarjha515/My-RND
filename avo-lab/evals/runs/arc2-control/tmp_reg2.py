rows=[l.strip() for l in open("grids/cur.txt") if len(l.strip())==64]
print("    "+"".join(str(x//10) for x in range(5,30)))
print("    "+"".join(str(x%10) for x in range(5,30)))
for y in range(33,50):
    print(f"{y:2d}  "+rows[y][5:30])
nines=[(y,x) for y in range(64) for x in range(64) if rows[y][x]=="9" and not (35<=y<=39 and 14<=x<=18)]
print("static nines:", sorted(set(nines)))
