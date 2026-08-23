import sys
from solution import is_balanced

CASES = [
    (r"()[]", True),
    (r"([)]", False),
    (r"{[()]}", True),
    ("'('", True),
    ("'(x)'(", False),
    ('\\"(', False),       # chars: \ "(  -> backslash escapes quote, no string opens; ( unpaired
    ('"\\("', True),       # chars: "\ (  -> string opens, \( escaped inside, unterminated tail
    ("'\\'(", True),       # chars: ' \' ( -> escaped \' keeps string open; tail ignored
    ("", True),
    ("\\", True),          # lone trailing backslash, nothing after
    ("\\)", True),         # escaped ) is neutral
    ("\"'\"", True),       # double-quoted contains single quote
    ("'\"'", True),        # single-quoted contains double quote
    ("(]", False),
    (")", False),
    ("(", False),
    ("a(b[c]{d}e)f", True),
    ("'unclosed", True),   # unterminated tail ignored
    ("'unclosed)(", True), # whole tail inside quote ignored
]

ok = True
for s, want in CASES:
    got = is_balanced(s)
    status = "OK " if got == want else "BAD"
    if got != want:
        ok = False
    print(f"{status} {s!r} -> {got} (want {want})")
sys.exit(0 if ok else 1)
