"""X5 - composed grid rule fixtures (examples + hidden inputs).

Rule (reference, kept here AND independently in the checker):
  R1: enclosed-region fill - every 4-connected region of 0s that does not
      touch the border and whose non-zero neighbours all share ONE colour c
      becomes c.
  R2: gravity - after R1, in every column all non-zero cells fall straight
      down, preserving their top-to-bottom order; zeros float up.
  Compose: apply R1 first, THEN R2.

Run from repo root: python avo-lab/tools/gen_x5.py
"""
from pathlib import Path

TASK = Path(__file__).resolve().parents[1] / "evals" / "tasks" / "x5-compose"


def g(*rows):
    return [list(map(int, r.split())) for r in rows]


def fill_enclosed(grid):
    rows, cols = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    seen = [[False] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not seen[r][c]:
                stack, region, borders, edge = [(r, c)], [], set(), False
                seen[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    region.append((cr, cc))
                    if cr in (0, rows - 1) or cc in (0, cols - 1):
                        edge = True
                    for nr, nc in ((cr+1, cc), (cr-1, cc), (cr, cc+1), (cr, cc-1)):
                        if 0 <= nr < rows and 0 <= nc < cols:
                            v = grid[nr][nc]
                            if v == 0 and not seen[nr][nc]:
                                seen[nr][nc] = True
                                stack.append((nr, nc))
                            elif v != 0:
                                borders.add(v)
                if not edge and len(borders) == 1:
                    col = next(iter(borders))
                    for cr, cc in region:
                        out[cr][cc] = col
    return out


def gravity(grid):
    rows, cols = len(grid), len(grid[0])
    out = [[0] * cols for _ in range(rows)]
    for c in range(cols):
        vals = [grid[r][c] for r in range(rows) if grid[r][c] != 0]
        for i, v in enumerate(vals):
            out[rows - len(vals) + i][c] = v
    return out


def compose(grid):
    return gravity(fill_enclosed(grid))


EXAMPLES = [
    # ex1: fill only (already compact columns -> gravity no-op)
    g("2 2 2 2 2 2",
      "2 0 0 0 2 0",
      "2 0 0 0 2 0",
      "2 2 2 2 2 0",
      "0 0 0 0 0 3",
      "3 0 0 0 0 3"),
    # ex2: gravity only (open regions untouched by R1)
    g("5 0 0 6 0 0",
      "0 0 0 6 0 0",
      "5 0 0 0 0 7",
      "0 0 4 0 0 0",
      "0 0 4 0 0 0",
      "9 9 4 9 0 9"),
    # ex3: BOTH rules, order matters: filled cell must END UP at column bottom
    g("1 1 1 1 1 0",
      "1 0 0 0 1 0",
      "1 0 0 0 1 8",
      "1 1 1 1 1 0",
      "0 0 0 0 0 0",
      "4 0 0 0 0 4"),
    # ex4: negative case (mixed-border region stays 0) + gravity of loose cells
    g("3 3 3 6 6 6",
      "3 0 0 0 6 0",
      "8 0 0 0 6 0",
      "8 0 0 5 0 0",
      "0 0 0 0 0 0",
      "2 0 0 0 0 1"),
]

INPUTS = [
    g("7 7 7 7 7 7 7 7",
      "7 0 0 0 0 0 0 7",
      "7 0 0 0 0 0 0 7",
      "7 0 0 0 0 0 0 7",
      "7 7 7 7 7 7 7 7",
      "0 0 0 0 0 0 0 0",
      "0 0 5 0 0 0 0 0",
      "0 0 0 0 0 0 3 0"),
    g("4 4 4 0 9 9 9 0",
      "4 0 0 0 9 0 0 6",
      "0 0 0 0 9 0 0 0",
      "2 2 2 0 0 0 0 6",
      "2 0 2 0 0 0 0 0",
      "2 2 2 0 0 0 0 0",
      "0 0 0 0 1 0 0 0",
      "0 0 0 0 0 0 0 1"),
    g("8 8 8 8 8 8 8 8",
      "8 0 0 0 0 0 0 8",
      "8 0 3 3 3 0 0 8",
      "8 0 3 0 3 0 0 8",
      "8 0 3 3 3 0 0 8",
      "8 0 0 0 0 0 0 8",
      "8 8 8 8 8 8 8 8",
      "6 0 0 0 0 0 0 6"),
]


def render(grid):
    return "\n".join(" ".join(map(str, row)) for row in grid) + "\n"


def main():
    parts = []
    for i, grid in enumerate(EXAMPLES, 1):
        parts.append(f"EXAMPLE {i} INPUT")
        parts.append(render(grid).rstrip("\n"))
        parts.append(f"EXAMPLE {i} OUTPUT")
        parts.append(render(compose(grid)).rstrip("\n"))
        parts.append("")
    (TASK / "examples.txt").write_text("\n".join(parts), encoding="utf-8")

    inp = TASK / "inputs"
    inp.mkdir(exist_ok=True)
    for i, grid in enumerate(INPUTS, 1):
        (inp / f"h{i}.txt").write_text(render(grid), encoding="utf-8")

    # sanity: examples are consistent with BOTH implementations? checker keeps
    # its own copy; agreement is asserted during self-test instead.
    print("x5 fixtures written")


if __name__ == "__main__":
    main()
