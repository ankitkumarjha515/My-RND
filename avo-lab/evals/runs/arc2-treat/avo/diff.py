import sys

def load(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read().splitlines()

def grid(lines):
    g = [l for l in lines if l and l[0] in "0123456789abcdef"]
    return g

def main(a, b):
    A, B = grid(load(a)), grid(load(b))
    if len(A) != len(B):
        print(f"ROWCOUNT {len(A)} vs {len(B)}")
    for i, (ra, rb) in enumerate(zip(A, B)):
        if ra != rb:
            cols = [j for j, (x, y) in enumerate(zip(ra, rb)) if x != y]
            # group consecutive
            groups = []
            start = prev = cols[0]
            for j in cols[1:]:
                if j == prev + 1:
                    prev = j
                else:
                    groups.append((start, prev)); start = prev = j
            groups.append((start, prev))
            desc = ", ".join(f"c{s}-{e}: {ra[s:e+1]}->{rb[s:e+1]}" for s, e in groups)
            print(f"r{i}: {desc}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
