import glob
def load(p): return [l.strip() for l in open(p) if len(l.strip())==64]
a=load("grids/s479_ACTION4.txt")   # step 20 = L2 start
b=load("grids/s489_ACTION3.txt")   # now, on diamond A
for y in range(64):
    if a[y]!=b[y]:
        print(f"row {y}:")
        print("  before:",a[y])
        print("  after :",b[y])
