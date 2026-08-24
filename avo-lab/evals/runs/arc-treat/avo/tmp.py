for name in ["f046","f048","f050","f051"]:
    rows=[l.rstrip("\n") for l in open(f"avo/{name}_act.txt",encoding="utf-8") if len(l.rstrip("\n"))>=64][:64]
    r61=rows[61]; r62=rows[62]
    print(name, "row61[40:]:", r61[40:], )
    print("     row62[40:]:", r62[40:])
