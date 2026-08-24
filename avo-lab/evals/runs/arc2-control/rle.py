import sys

def load(p):
    rows = []
    for line in open(p):
        line = line.rstrip("\n")
        if len(line) == 64 and all(c in "0123456789abcdef" for c in line.lower()):
            rows.append(line)
    return rows

rows = load(sys.argv[1])
for y, r in enumerate(rows):
    runs = []
    prev = r[0]
    n = 0
    start = 0
    for x, ch in enumerate(r + "\0"):
        if ch == prev:
            n += 1
        else:
            if n >= 2 or prev not in "3":
                runs.append(f"{prev}x{n}@{start}")
            else:
                runs.append(f"{prev}@{start}")
            start = x
            prev = ch
            n = 1
    print(f"{y:3d} " + " ".join(runs))
