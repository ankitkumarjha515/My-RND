"""H2 checker — grid rule inference. Usage: python h2_checker.py <task_dir>

Independent re-implementation of the rule (deliberately written separately
from tools/gen_h2.py so a shared bug cannot silently validate itself).
"""
import sys
from pathlib import Path


def transform(grid):
    rows, cols = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    seen = [[False] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not seen[r][c]:
                queue = [(r, c)]
                seen[r][c] = True
                region = []
                border_colors = set()
                touches_edge = False
                while queue:
                    cr, cc = queue.pop(0)
                    region.append((cr, cc))
                    if cr in (0, rows - 1) or cc in (0, cols - 1):
                        touches_edge = True
                    for nr, nc in ((cr + 1, cc), (cr - 1, cc),
                                   (cr, cc + 1), (cr, cc - 1)):
                        if 0 <= nr < rows and 0 <= nc < cols:
                            v = grid[nr][nc]
                            if v == 0:
                                if not seen[nr][nc]:
                                    seen[nr][nc] = True
                                    queue.append((nr, nc))
                            else:
                                border_colors.add(v)
                if not touches_edge and len(border_colors) == 1:
                    fill = next(iter(border_colors))
                    for cr, cc in region:
                        out[cr][cc] = fill
    return out


def parse(path: Path):
    text = path.read_text(encoding="utf-8").strip()
    rows = [list(map(int, line.split())) for line in text.splitlines() if line.strip()]
    width = len(rows[0])
    if any(len(r) != width for r in rows):
        raise ValueError("ragged grid")
    return rows


def main():
    task = Path(sys.argv[1])
    results = []
    total = 0

    for i in (1, 2, 3):
        name = f"grid-h{i}"
        inp = task / "inputs" / f"h{i}.txt"
        out = task / "outputs" / f"h{i}_out.txt"
        try:
            want = transform(parse(inp))
            got = parse(out)
            ok = got == want
            detail = "exact match"
            if not ok:
                same = sum(
                    1
                    for gr, wr in zip(got, want)
                    for gc, wc in zip(gr, wr)
                    if gc == wc
                )
                cells = sum(len(w) for w in want)
                detail = f"{same}/{cells} cells correct (or wrong shape)"
        except FileNotFoundError as exc:
            ok = False
            detail = f"missing file: {exc.filename}"
        except (ValueError, IndexError) as exc:
            ok = False
            detail = f"bad format: {exc}"
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    weights = [33, 33, 34]
    score = sum(w for (_, ok), w in zip(results, weights) if ok)
    total_ok = all(ok for _, ok in results)
    if total_ok:
        score = 100
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
