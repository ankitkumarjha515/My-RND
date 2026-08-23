"""Generates the x4 corpus deterministically. Run from repo root:
python avo-lab/tools/gen_x4.py
"""
import random
from pathlib import Path

TASK = Path(__file__).resolve().parents[1] / "evals" / "tasks" / "x4-corpus"

CONS = "bcdfghjklmnpqrstvwxyz"
VOW = "aeiou"


def word(rng):
    n = rng.randint(2, 9)
    w = "".join(rng.choice(CONS if i % 2 == 0 else VOW) for i in range(n))
    roll = rng.random()
    if roll < 0.10 and len(w) >= 2:          # inject doubled letter
        pos = rng.randint(0, len(w) - 2)
        w = w[:pos] + w[pos] * 2 + w[pos + 2:]
    if roll > 0.93:                          # inject q NOT followed by u
        pos = rng.randint(0, len(w) - 1)
        w = w[:pos] + "q" + w[pos + 1:]
    return w


def line(rng):
    parts = []
    for _ in range(rng.randint(6, 12)):
        r = rng.random()
        if r < 0.12:
            parts.append(str(rng.randint(0, 99999)))
        elif r < 0.16:
            parts.append(f"{word(rng)}!{rng.randint(1, 90)}")
        else:
            parts.append(word(rng))
    s = " ".join(parts)
    if rng.random() < 0.25:
        s += "," 
    if rng.random() < 0.15:
        s += " q"                      # bare q token
    return s


if __name__ == "__main__":
    rng = random.Random(20260822)
    text = "\n".join(line(rng) for _ in range(220)) + "\n"
    TASK.mkdir(parents=True, exist_ok=True)
    (TASK / "corpus.txt").write_text(text, encoding="utf-8")
    print(f"corpus written: {len(text)} chars")
