rows = [l.rstrip("\n") for l in open("avo/f018_act.txt", encoding="utf-8") if len(l.rstrip("\n"))>=64][:64]
print("bottom-left room now:")
for y in range(53,63): print(f"{y:2d} {rows[y][:13]}")
print("top-right room now:")
for y in range(8,17): print(f"{y:2d} {rows[y][30:43]}")
