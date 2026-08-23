"""M1 checker — quoted-bracket validator. Usage: python m1_checker.py <task_dir>

Cases are built from explicit char tokens to avoid source-escaping ambiguity.
"""
import importlib.util
import sys
from pathlib import Path

Q, DQ, BS = "'", '"', "\\"
B = {  # bracket chars
    "(": "open", ")": "close", "[": "open", "]": "close",
    "{": "open", "}": "close",
}
PAIRS = {")": "(", "]": "[", "}": "{"}


def reference(s: str) -> bool:
    """Independent implementation of the README contract."""
    depth = []
    quote = None  # None or the active quote char
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if BS == c and i + 1 < n:
            i += 2  # escaped char is fully neutral (even inside quotes)
            continue
        if quote is not None:
            if c == quote:
                quote = None
        elif c in (Q, DQ):
            quote = c
        elif c in B:
            if c in PAIRS:
                if not depth or depth[-1] != PAIRS[c]:
                    return False
                depth.pop()
            else:
                depth.append(c)
        i += 1
    return not depth


def C(*tokens):
    """Join char tokens into a string; multi-char plain words are split."""
    out = []
    for t in tokens:
        for ch in t:
            out.append(ch)
    return "".join(out)


GROUPS = [
    ("basic-balance", 20, [
        (C(""), True), (C("()"), True), (C("()[]"), True),
        (C("{[()]}"), True), (C("("), False), (C(")"), False), (C(")("), False),
    ]),
    ("nesting-interleaving", 20, [
        (C("([)]"), False), (C("((()))"), True), (C("(()"), False),
        (C("{[}]"), False), (C("a(b)c[d]e{f}g"), True), (C("(]"), False),
        (C("[]{}()"), True),
    ]),
    ("quotes-swallow", 20, [
        (C(Q, "("), True),                       # '(   unterminated swallows (
        (C(DQ, "(", DQ), True),                  # "("  closed string hides (
        (C(Q, "(x)", Q, "("), False),            # '(x)'(  trailing bare (
        (C(DQ, Q, "(", Q, DQ), True),            # "'('" nested other-quote inside
        (C(Q, "it", Q, "s ("), False),           # apostrophe trap: it's (
        (C(DQ, "(", Q), True),                   # unterminated double-quote tail
        (C("x", Q, ")", Q, "y("), False),        # ')'( -> trailing (
    ]),
    ("escapes", 20, [
        (C(BS, BS), True),                       # \\ two literal backslashes
        (C(BS, DQ, "("), False),                 # \" never opens a string; ( unpaired
        (C(Q, BS, Q, Q, "("), False),            # '\' then ( outside -> unpaired
        (C(Q, BS, Q, Q, BS, Q, Q), True),        # all quotes neutralized/closed tails
        (C("a", BS, "(", "b", BS, ")", "c"), True),   # escaped brackets are neutral
        (C(BS, Q, "(", Q), True),                # \" opens nothing... wait: see below
    ]),
    ("unterminated-tails", 20, [
        (C(Q, "hello world"), True),
        (C(DQ, "["), True),
        (C("(", Q, "a"), False),                 # ( opened before string counts
        (C(Q, "x", Q, "y("), False),
        (C("}"), False),
        (C("[", Q, "]"), False),                 # [ opened BEFORE string -> unpaired
    ]),
]

# fix case escapes-6 manually: chars are  \  '  (  '  -> \ escapes the opening
# quote so the string never starts; ( unpaired -> False.
GROUPS[3][2][5] = (C(BS, Q, "(", Q), False)


def main():
    task = Path(sys.argv[1])
    results = []

    def grp(name, ok, detail=""):
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    mod = None
    sol = task / "solution.py"
    if sol.exists():
        try:
            spec = importlib.util.spec_from_file_location("solution", sol)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as exc:  # noqa: BLE001 — checker must survive any solution
            grp("imports", False, f"{type(exc).__name__}: {exc}")
    if mod is None and not results:
        grp("imports", False, "solution.py missing")
    if mod is not None and not any(n == "imports" for n, _ in results):
        grp("imports", True)

    fn = getattr(mod, "is_balanced", None) if mod else None
    if not callable(fn):
        grp("has-is-balanced", False, "callable is_balanced(s) not found")
        grp("battery", False)
        battery_ok = {}
    else:
        grp("has-is-balanced", True)
        battery_ok = {}
        bad = []
        for name, weight, cases in GROUPS:
            group_ok = True
            for s, want in cases:
                try:
                    got = fn(s)
                    ref = reference(s)
                    # cross-check our expectation against the reference impl
                    if got != want or ref != want:
                        group_ok = False
                        bad.append((repr(s), want, got, ref))
                except Exception as exc:  # noqa: BLE001
                    group_ok = False
                    bad.append((repr(s), want, f"raised {type(exc).__name__}", "-"))
            battery_ok[name] = group_ok
            grp(name, group_ok,
                "" if group_ok else f"first failures: {bad[:3]}")

    score = sum(w for name, w, _ in GROUPS if battery_ok.get(name))
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
