"""X5 checker - composed grid rule. Usage: python x5_checker.py <task_dir>

Independent implementation: R1 (enclosed single-color fill) THEN
R2 (gravity: non-zero cells fall to column bottoms, order preserved).
"""
import sys
from pathlib import Path


def fill_enclosed(grid):
    rows, cols = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    seen = [[False] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not seen[r][c]:
                queue, region, borders, edge = [(r, c)], [], set(), False
                seen[r][c] = True
                while queue:
                    cr, cc = queue.pop(0)
                    region.append((cr, cc))
                    if cr in (0, rows - 1) or cc in (0, cols - 1):
                        edge = True
                    for nr, nc in ((cr+1, cc), (cr-1, cc), (cr, cc+1), (cr, cc-1)):
                        if 0 <= nr < rows and 0 <= nc < cols:
                            v = grid[nr][nc]
                            if v == 0:
                                if not seen[nr][nc]:
                                    seen[nr][nc] = True
                                    queue.append((nr, nc))
                            else:
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


def transform(grid):
    return gravity(fill_enclosed(grid))


def parse(path: Path):
    rows = [list(map(int, line.split()))
            for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows or any(len(r) != len(rows[0]) for r in rows):
        raise ValueError("bad grid shape")
    return rows


def main():
    task = Path(sys.argv[1])
    results = []

    for i in (1, 2, 3):
        name = f"grid-h{i}"
        try:
            want = transform(parse(task / "inputs" / f"h{i}.txt"))
            got = parse(task / "outputs" / f"h{i}_out.txt")
            ok = got == want
            detail = "exact match"
            if not ok:
                same = sum(1 for gr, wr in zip(got, want)
                           for gc, wc in zip(gr, wr) if gc == wc)
                cells = sum(len(w) for w in want)
                detail = f"{same}/{cells} cells match"
        except FileNotFoundError as exc:
            ok = False
            detail = f"missing file: {exc.filename}"
        except (ValueError, IndexError) as exc:
            ok = False
            detail = f"bad format: {exc}"
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    score = 100 if all(ok for _, ok in results) else sum(
        w for (_, ok), w in zip(results, (34, 33, 33)) if ok)
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
