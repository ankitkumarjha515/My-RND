import glob
files=sorted(glob.glob("grids/s4*.txt"))
def load(p): return [l.strip() for l in open(p) if len(l.strip())==64]
a=load([f for f in files if "ACTION1" in f and "s46" + "1" in f][0])  # step20 L2 start (s461)
b=load(files[-1])
print("now:",files[-1])
for y in [15,16,17,18,51,52,53]:
    if a[y]!=b[y]:
        print(f"row {y}:"); print("  before:",a[y][10:55]); print("  after :",b[y][10:55])
for y in [61,62]:
    print(f"fuse{y} before:",a[y][10:58]); print(f"fuse{y} after :",b[y][10:58])
