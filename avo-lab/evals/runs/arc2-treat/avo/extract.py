import importlib.util, sys, json

SRC = r"environment_files\ls20\9607627b\ls20.py"
spec = importlib.util.spec_from_loader("ls20mod", loader=None)
mod = importlib.util.module_from_spec(spec)
src = open(SRC, encoding="utf-8").read()
exec(compile(src, SRC, "exec"), mod.__dict__)

lv = mod.levels[0]
print("=== LEVEL DATA ===")
for k, v in (lv._data or {}).items():
    print(f"{k}: {v}")

print("\n=== SPRITES BY TAG ===")
groups = {}
for s in lv._sprites:
    tags = tuple(sorted(s.tags)) if s.tags else ("(none)",)
    groups.setdefault(tags, []).append(s)

for tags, ss in sorted(groups.items(), key=lambda kv: str(kv[0])):
    print(f"\nTAGS {tags}  x{len(ss)}")
    if len(ss) <= 12:
        for s in ss:
            print(f"   {s.name} pos=({s.x},{s.y}) size={s.width}x{s.height}")
    else:
        poss = [(s.x, s.y) for s in ss]
        print(f"   positions: {poss}")

# avatar
av = lv.get_sprites_by_tag("sfqyzhzkij")
print("\navatar:", [(s.name, s.x, s.y, s.width, s.height) for s in av])

# shapes
print("\n=== SHAPE TEMPLATES ===")
names = ["gngifvjddu", "fywfjzkxlm", "mkfbgalsbe", "nnjhdcanjk", "grcpfuizfp", "ubspnhafvq"]
for i, n in enumerate(names):
    sp = mod.sprites[n]
    rows = ["".join("#" if v >= 0 else "." for v in row) for row in sp.pixels]
    print(f"shape{i} {n}:")
    for r in rows:
        print("   ", r)
