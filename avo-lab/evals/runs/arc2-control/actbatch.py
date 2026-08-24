import subprocess,sys
from pathlib import Path
acts=sys.argv[1:]
for a in acts:
    Path("resp.txt").unlink(missing_ok=True)
    Path("cmd.txt").write_text(f"ACT {a}")
    import time; t0=time.time()
    while not Path("resp.txt").exists():
        if time.time()-t0>70: print("SLOW",a); break
        time.sleep(1)
    txt=Path("resp.txt").read_text().splitlines()
    meta=[l for l in txt if l.startswith("step=")][0]
    n=len(list(Path("grids").glob("s*.txt")))+1
    Path(f"grids/s{300+n}_{a}.txt").write_text("\n".join(txt))
    print(a,"->",meta)
