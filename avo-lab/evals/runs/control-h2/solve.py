import sys
from collections import deque
from pathlib import Path


def parse_grid(text):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append([int(x) for x in line.split()])
    return rows


def format_grid(grid):
    return "\n".join(" ".join(str(v) for v in row) for row in grid) + "\n"


def solve(grid):
    h, w = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    outside = [[False] * w for _ in range(h)]
    q = deque()

    def bfs_zero(start_i, start_j, mark):
        region = []
        qq = deque([(start_i, start_j)])
        mark[start_i][start_j] = True
        while qq:
            i, j = qq.popleft()
            region.append((i, j))
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = i + di, j + dj
                if (
                    0 <= ni < h
                    and 0 <= nj < w
                    and not mark[ni][nj]
                    and grid[ni][nj] == 0
                ):
                    mark[ni][nj] = True
                    qq.append((ni, nj))
        return region

    for i in range(h):
        for j in range(w):
            if (i in (0, h - 1) or j in (0, w - 1)) and grid[i][j] == 0 and not outside[i][j]:
                bfs_zero(i, j, outside)

    visited = [[False] * w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            if grid[i][j] == 0 and not outside[i][j] and not visited[i][j]:
                region = bfs_zero(i, j, visited)
                border_colors = set()
                for ci, cj in region:
                    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ni, nj = ci + di, cj + dj
                        if 0 <= ni < h and 0 <= nj < w and grid[ni][nj] != 0:
                            border_colors.add(grid[ni][nj])
                if len(border_colors) == 1:
                    fill = next(iter(border_colors))
                    for ci, cj in region:
                        out[ci][cj] = fill
    return out


def main():
    base = Path(__file__).parent
    for name in ("h1", "h2", "h3"):
        src = base / "inputs" / f"{name}.txt"
        dst_dir = base / "outputs"
        dst_dir.mkdir(exist_ok=True)
        grid = parse_grid(src.read_text())
        result = solve(grid)
        (dst_dir / f"{name}_out.txt").write_text(format_grid(result))
        print(f"wrote {name}: {len(result)}x{len(result[0])}")


if __name__ == "__main__":
    main()
