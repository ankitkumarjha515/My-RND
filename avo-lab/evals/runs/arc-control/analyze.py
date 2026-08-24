import sys, re
from collections import deque

def load(path):
    rows = []
    meta = {}
    for line in open(path):
        line = line.rstrip('\n')
        m = re.match(r'^(\d+) ([453bc901]+)$', line)
        if m and len(m.group(2)) >= 40:
            rows.append((int(m.group(1)), m.group(2)))
            continue
        if re.match(r'^[453bc901]{40,}$', line):
            rows.append((len(rows), line))
            continue
        if '=' in line:
            k, v = line.split('=', 1)
            meta[k] = v
    g = {}
    for r, s in rows:
        for c, ch in enumerate(s):
            g[(r, c)] = ch
    return g, meta

def assembly(g):
    for r in sorted(set(r for r, c in g)):
        s = ''.join(g.get((r, c), '?') for c in range(0, 70))
        i = s.find('ccccc')
        if i >= 0:
            return (r, i)
    return None

PASS = set('3b0')

def passable(g, r, c):
    for dr in range(5):
        for dc in range(5):
            ch = g.get((r + dr, c + dc))
            if ch is None:
                return False
            if ch == 'b' and (r + dr) < 45:
                pass  # ring cells walkable
            if ch not in PASS:
                return False
    return True

def bfs(g, start):
    dist = {start: (None, None)}
    q = deque([start])
    while q:
        r, c = q.popleft()
        for sym, (dr, dc) in (('1', (-5, 0)), ('2', (5, 0)), ('3', (0, -5)), ('4', (0, 5))):
            nr, nc = r + dr, c + dc
            if (nr, nc) in dist:
                continue
            if passable(g, nr, nc):
                dist[(nr, nc)] = ((r, c), sym)
                q.append((nr, nc))
    return dist

def path(dist, goal):
    seq = []
    cur = goal
    while dist[cur][0] is not None:
        prev, sym = dist[cur]
        seq.append(sym)
        cur = prev
    return ''.join(reversed(seq))

def main():
    g, meta = load(sys.argv[1])
    a = assembly(g)
    print('meta:', {k: v for k, v in meta.items() if k in ('step', 'state', 'levels')})
    print('assembly cargo top-left:', a)
    # digits (switch glyphs)
    digs = [(r, c, ch) for (r, c), ch in sorted(g.items()) if ch in '01' and r < 60]
    print('digit cells:', digs)
    # rings
    rings = [(r, c) for (r, c), ch in sorted(g.items()) if ch == 'b' and r < 60]
    print('ring cells:', rings)
    # bar
    barr = max(r for r, c in g)
    bar = sum(1 for (r, c), ch in g.items() if ch == 'b')
    print('total b cells (bar+rings):', bar)
    if a:
        dist = bfs(g, a)
        print('reachable positions:', len(dist))
        targets = {}
        for (r, c, ch) in digs:
            best = None
            for dr in range(-4, 5):
                for dc in range(-4, 5):
                    p = (r + dr, c + dc)
                    if p in dist:
                        d = abs(dr) + abs(dc)
                        if best is None or d < best[0]:
                            best = (d, p, path(dist, p))
            targets[(r, c, ch)] = best
        for k, v in targets.items():
            print('switch', k, '->', v)

if __name__ == '__main__':
    main()
