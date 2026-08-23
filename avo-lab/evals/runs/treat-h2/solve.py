import os

BASE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    with open(path) as f:
        return [[int(x) for x in line.split()] for line in f if line.strip()]


def save(path, grid):
    with open(path, "w") as f:
        for row in grid:
            f.write(" ".join(str(v) for v in row) + "\n")


def transform(grid):
    R, C = len(grid), len(grid[0])
    zeros = [(r, c) for r in range(R) for c in range(C) if grid[r][c] == 0]
    seen = set()
    out = [row[:] for row in grid]
    for start in zeros:
        if start in seen:
            continue
        comp = []
        stack = [start]
        seen.add(start)
        while stack:
            r, c = stack.pop()
            comp.append((r, c))
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 0 and (nr, nc) not in seen:
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        if any(r in (0, R - 1) or c in (0, C - 1) for r, c in comp):
            continue
        adj_colors = set()
        for r, c in comp:
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] != 0:
                    adj_colors.add(grid[nr][nc])
        if len(adj_colors) == 1:
            fill = adj_colors.pop()
            for r, c in comp:
                out[r][c] = fill
    return out


os.makedirs(os.path.join(BASE, "outputs"), exist_ok=True)

for name in ("h1", "h2", "h3"):
    g = load(os.path.join(BASE, "inputs", name + ".txt"))
    save(os.path.join(BASE, "outputs", name + "_out.txt"), transform(g))
print("done")
