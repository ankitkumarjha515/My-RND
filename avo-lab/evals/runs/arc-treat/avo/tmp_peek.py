import sys
rows = [l.rstrip("\n") for l in open("avo/f017_act.txt", encoding="utf-8") if len(l.rstrip("\n"))>=64]
for y0,y1,x0,x1,t in [(8,17,30,42,"top-right room"),(53,63,0,63,"bottom strip")]:
    print(f"--- {t}")
    for y in range(y0,y1+1):
        print(f"{y:2d} {rows[y][x0:x1+1] if x1<64 else rows[y][x0:]}"[:80])
