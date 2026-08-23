"""Generates h2-grid-transform fixtures (examples + hidden inputs).

Deterministic, hand-designed grids. Run from repo root:
python avo-lab/tools/gen_h2.py
"""
from pathlib import Path

TASK = Path(__file__).resolve().parents[1] / "evals" / "tasks" / "h2-grid-transform"


def g(*rows):
    return [list(map(int, r.split())) for r in rows]


EXAMPLES = [
    (  # ex1: enclosed by 3 -> filled; outer zeros touch border -> untouched
        g("3 3 3 3 3 0",
          "3 0 0 0 3 0",
          "3 0 0 0 3 0",
          "3 0 0 0 3 0",
          "3 3 3 3 3 0",
          "0 0 0 0 0 0"),
    ),
    (  # ex2: enclosed by 7 -> filled; open area stays
        g("0 0 0 0 0 0",
          "0 7 7 7 7 0",
          "0 7 0 0 7 0",
          "0 7 0 0 7 5",
          "0 7 7 7 5 0",
          "0 0 0 5 0 0"),
    ),
    (  # ex3: two enclosures (2 and 5); edge-touching zero stays
        g("2 2 2 5 5 5",
          "2 0 2 5 0 5",
          "2 2 2 5 5 5",
          "0 0 0 0 0 0",
          "8 8 8 8 8 8",
          "8 0 8 0 1 1"),
    ),
    (  # ex4: NEGATIVE case — region bordered by two colors is NOT modified
        g("4 4 4 9 9 9",
          "4 0 0 0 9 9",
          "9 0 0 0 4 9",
          "9 0 0 0 9 9",
          "9 9 9 9 9 9",
          "0 0 0 0 0 0"),
    ),
]

INPUTS = [
    g("6 6 6 6 6 6 6",
      "6 0 0 0 0 0 6",
      "6 0 0 0 0 0 6",
      "6 0 0 0 0 0 6",
      "6 6 6 6 6 6 6",
      "0 0 0 0 0 0 0",
      "0 0 0 0 0 3 0"),
    g("1 1 1 0 4 4 4",
      "1 0 1 0 4 0 4",
      "1 1 1 0 4 0 4",
      "0 0 0 0 4 4 4",
      "2 2 2 0 0 0 0",
      "2 0 2 0 5 5 5",
      "2 2 2 0 5 0 5"),
    g("1 1 1 1 1 1 1",
      "1 0 0 0 0 0 1",
      "1 0 2 2 2 0 1",
      "1 0 2 0 2 0 1",
      "1 0 2 2 2 0 1",
      "1 0 0 0 0 0 1",
      "1 1 1 1 1 1 1"),
]


def render(grid):
    return "\n".join(" ".join(map(str, row)) for row in grid) + "\n"


def transform(grid):
    """Independent reference implementation of the intended rule.

    Zero-regions (4-connected) that do not touch the grid border and whose
    non-zero neighbors share a single color are recolored to that color.
    """
    rows, cols = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    seen = [[False] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not seen[r][c]:
                stack, region, borders, touches_edge = [(r, c)], [], set(), False
                seen[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    region.append((cr, cc))
                    if cr in (0, rows - 1) or cc in (0, cols - 1):
                        touches_edge = True
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if not (0 <= nr < rows and 0 <= nc < cols):
                            continue
                        v = grid[nr][nc]
                        if v == 0:
                            if not seen[nr][nc]:
                                seen[nr][nc] = True
                                stack.append((nr, nc))
                        else:
                            borders.add(v)
                if not touches_edge and len(borders) == 1:
                    color = borders.pop()
                    for cr, cc in region:
                        out[cr][cc] = color
    return out


def main():
    parts = []
    for i, (grid,) in enumerate(EXAMPLES, 1):
        parts.append(f"EXAMPLE {i} INPUT")
        parts.append(render(grid).rstrip("\n"))
        parts.append(f"EXAMPLE {i} OUTPUT")
        parts.append(render(transform(grid)).rstrip("\n"))
        parts.append("")
    (TASK / "examples.txt").write_text("\n".join(parts), encoding="utf-8")

    inp_dir = TASK / "inputs"
    inp_dir.mkdir(exist_ok=True)
    for i, grid in enumerate(INPUTS, 1):
        (inp_dir / f"h{i}.txt").write_text(render(grid), encoding="utf-8")
    print("h2 fixtures written")


if __name__ == "__main__":
    main()
