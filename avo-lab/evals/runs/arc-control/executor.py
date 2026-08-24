import subprocess, sys, re

PY = r"C:\Users\ankit kumar jha\Desktop\all folder inside this\cool-project\Reach-out\avo-lab\vendor\arcvenv\Scripts\python.exe"
SYM = {'1': 'ACTION1', '2': 'ACTION2', '3': 'ACTION3', '4': 'ACTION4'}

def run_act(sym):
    p = subprocess.run([PY, 'driver.py', 'client', 'ACT', SYM[sym]],
                       capture_output=True, text=True)
    return p.stdout

def parse(out):
    pos = None
    step = lev = None
    lines = out.splitlines()
    for i, ln in enumerate(lines):
        j = ln.find('ccccc')
        if j >= 0 and pos is None:
            pos = (i, j)
        m = re.match(r'step=(\d+) state=(\S+) levels=(\d+)/', ln)
        if m:
            step, lev = int(m.group(1)), int(m.group(3))
    return pos, step, lev, out

def main():
    routeFile, prefix = sys.argv[1], sys.argv[2]
    route = open(routeFile).read().strip()
    expected = None
    if len(sys.argv) > 3:
        expected = [tuple(map(int, x.split(','))) for x in sys.argv[3].split(';')]
    log = []
    for k, sym in enumerate(route):
        out = run_act(sym)
        pos, step, lev, txt = parse(out)
        ok = ''
        if expected and k + 1 < len(expected) and pos != expected[k + 1]:
            ok = 'MISMATCH expected %s' % (expected[k + 1],)
        fn = '%s%03d.txt' % (prefix, k)
        with open(fn, 'w') as f:
            f.write(txt)
        print('%s step=%s pos=%s lev=%s %s' % (fn, step, pos, lev, ok))
        log.append((fn, step, pos, lev))
        if lev and lev > 1:
            print('LEVEL UP!')
            break
        if ok:
            break
        if pos is None:
            print('NO ASSEMBLY IN RESPONSE - stopping')
            break

main()
