"""X1 checker - Zigbus protocol. Usage: python x1_checker.py <task_dir>"""
import importlib.util
import sys
from pathlib import Path

HEX = set("0123456789ABCDEF")


def valid_key(k):
    return isinstance(k, str) and len(k) == 4 and all(ch in HEX for ch in k)


def int_token(tok):
    if not tok or not tok.isdigit():
        return None
    return int(tok)


def reference(events):
    out = []
    state = "DOWN"
    seq = 0
    oflow = 0
    key = None
    for ev in events:
        parts = ev.split(" ")
        head = parts[0] if parts else ""
        arg = parts[1] if len(parts) > 1 else ""
        if head == "OPEN":
            if not valid_key(arg):
                out.append("ERR BAD-KEY")
            elif state != "DOWN":
                out.append("ERR BUSY")
            else:
                state, seq, oflow, key = "UP", 0, 0, arg
                out.append("WELCOME")
        elif head == "SEND":
            n = int_token(arg)
            if n is None:
                out.append("ERR BAD-N")
            elif state == "UP":
                total = seq + n
                new = total % 65536
                if total >= 65536:
                    oflow = 1
                seq = new
                out.append("NAK OFLOW" if oflow == 1 else f"ACK {seq}")
            elif state == "WAIT":
                out.append("DEFERRED")
            else:
                out.append("ERR CLOSED")
        elif head == "PARK":
            if state == "DOWN":
                out.append("ERR CLOSED")
            else:
                state = "WAIT"
                out.append("PARKED")
        elif head == "RESUME":
            if not valid_key(arg):
                out.append("ERR BAD-KEY")
            elif state == "DOWN":
                out.append("ERR CLOSED")
            elif state == "UP":
                out.append("ERR ACTIVE")
            elif arg == key:
                state = "UP"
                out.append("RESUMED")
            else:
                out.append("ERR BAD-KEY")
        elif head == "RESET":
            state, seq, oflow, key = "DOWN", 0, 0, None
            out.append("RESET-OK")
        elif head == "CLOSE":
            if state == "DOWN":
                pass
            else:
                state = "DOWN"
                out.append("BYE")
        else:
            out.append("ERR UNKNOWN")
    out.append(f"SEQ {seq} OFLOW {oflow}")
    return out


E = lambda *lines: list(lines)

GROUPS = [
    ("lifecycle-open-close", 20, [
        ([], E("SEQ 0 OFLOW 0")),
        (["CLOSE"], E("SEQ 0 OFLOW 0")),                       # silent CLOSE when DOWN
        (["OPEN 12ab"], E("ERR BAD-KEY", "SEQ 0 OFLOW 0")),    # lowercase hex invalid
        (["OPEN ABCD"], E("WELCOME", "SEQ 0 OFLOW 0")),
        (["OPEN ABCD", "OPEN EEEE"], E("WELCOME", "ERR BUSY", "SEQ 0 OFLOW 0")),
        (["OPEN AB_CD"], E("ERR BAD-KEY", "SEQ 0 OFLOW 0")),
        (["OPEN ABCD", "CLOSE"], E("WELCOME", "BYE", "SEQ 0 OFLOW 0")),
        # key/seq survive CLOSE; but OPEN over them resets cleanly
        (["OPEN ABCD", "SEND 5", "CLOSE", "OPEN F00F"],
         E("WELCOME", "ACK 5", "BYE", "WELCOME", "SEQ 0 OFLOW 0")),
    ]),
    ("send-wrap-oflow", 30, [
        (["OPEN ABCD", "SEND 65535"], E("WELCOME", "ACK 65535", "SEQ 65535 OFLOW 0")),
        (["OPEN ABCD", "SEND 65535", "SEND 1"],
         E("WELCOME", "ACK 65535", "NAK OFLOW", "SEQ 0 OFLOW 1")),
        # NAK still advances seq: next SEND acks the newer value
        (["OPEN ABCD", "SEND 65535", "SEND 1", "SEND 2"],
         E("WELCOME", "ACK 65535", "NAK OFLOW", "NAK OFLOW", "SEQ 2 OFLOW 1")),
        # RESET clears oflow and returns to DOWN: SEND needs a fresh OPEN
        (["OPEN ABCD", "SEND 65535", "SEND 1", "RESET", "SEND 3"],
         E("WELCOME", "ACK 65535", "NAK OFLOW", "RESET-OK",
           "ERR CLOSED", "SEQ 0 OFLOW 0")),
        (["OPEN ABCD", "SEND 65535", "SEND 1", "RESET", "OPEN BEEF", "SEND 3"],
         E("WELCOME", "ACK 65535", "NAK OFLOW", "RESET-OK",
           "WELCOME", "ACK 3", "SEQ 3 OFLOW 0")),
        # huge n wraps repeatedly; carry sets oflow so output is NAK even on land-0
        (["OPEN ABCD", "SEND 131072"], E("WELCOME", "NAK OFLOW", "SEQ 0 OFLOW 1")),
        (["OPEN ABCD", "SEND -5"], E("WELCOME", "ERR BAD-N", "SEQ 0 OFLOW 0")),
        (["OPEN ABCD", "SEND 7x"], E("WELCOME", "ERR BAD-N", "SEQ 0 OFLOW 0")),
    ]),
    ("park-resume", 20, [
        (["RESUME ABCD"], E("ERR CLOSED", "SEQ 0 OFLOW 0")),
        (["OPEN ABCD", "RESUME ABCD"], E("WELCOME", "ERR ACTIVE", "SEQ 0 OFLOW 0")),
        (["OPEN ABCD", "PARK", "SEND 4"],
         E("WELCOME", "PARKED", "DEFERRED", "SEQ 0 OFLOW 0")),
        (["OPEN ABCD", "PARK", "RESUME ABCD", "SEND 9"],
         E("WELCOME", "PARKED", "RESUMED", "ACK 9", "SEQ 9 OFLOW 0")),
        (["OPEN ABCD", "PARK", "RESUME FFFF"],
         E("WELCOME", "PARKED", "ERR BAD-KEY", "SEQ 0 OFLOW 0")),  # stays WAIT
        (["OPEN ABCD", "PARK", "RESUME FFFF", "RESUME ABCD", "SEND 2"],
         E("WELCOME", "PARKED", "ERR BAD-KEY", "RESUMED", "ACK 2", "SEQ 2 OFLOW 0")),
        # lowercase key fails even when it 'matches' visually
        (["OPEN ABCD", "PARK", "RESUME abcd"],
         E("WELCOME", "PARKED", "ERR BAD-KEY", "SEQ 0 OFLOW 0")),
    ]),
    ("error-priority-format", 20, [
        # malformed argument beats wrong-state error
        (["SEND xx", "SEND 5"], E("ERR BAD-N", "ERR CLOSED", "SEQ 0 OFLOW 0")),
        (["RESUME zz!"], E("ERR BAD-KEY", "SEQ 0 OFLOW 0")),
        (["FLY 7"], E("ERR UNKNOWN", "SEQ 0 OFLOW 0")),
        (["PING"], E("ERR UNKNOWN", "SEQ 0 OFLOW 0")),
        # CLOSE in DOWN emits nothing at all - not even blank lines
        (["CLOSE", "CLOSE", "OPEN ABCD", "CLOSE", "CLOSE"],
         E("WELCOME", "BYE", "SEQ 0 OFLOW 0")),
    ]),
    ("state-persistence", 10, [
        # seq persists across PARK/RESUME; CLOSE keeps seq until next OPEN
        (["OPEN ABCD", "SEND 100", "PARK", "RESUME ABCD", "SEND 50"],
         E("WELCOME", "ACK 100", "PARKED", "RESUMED", "ACK 150", "SEQ 150 OFLOW 0")),
        # after CLOSE without OPEN, SEND is ERR CLOSED; seq retained in footer
        (["OPEN ABCD", "SEND 300", "CLOSE", "SEND 1"],
         E("WELCOME", "ACK 300", "BYE", "ERR CLOSED", "SEQ 300 OFLOW 0")),
    ]),
]


def main():
    task = Path(sys.argv[1])
    results = []

    def grp(name, ok, detail=""):
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    mod = None
    sol = task / "interpreter.py"
    if sol.exists():
        try:
            spec = importlib.util.spec_from_file_location("zb_interp", sol)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as exc:  # noqa: BLE001
            grp("imports", False, f"{type(exc).__name__}: {exc}")
    if mod is None and not results:
        grp("imports", False, "interpreter.py missing")

    fn = getattr(mod, "run", None) if mod else None
    if not callable(fn):
        grp("has-run", False)
        for name, _, _ in GROUPS:
            grp(name, False)
    else:
        grp("has-run", True)
        bad = []
        for name, w, cases in GROUPS:
            gok = True
            for events, want in cases:
                try:
                    got = fn(list(events))
                    ref = reference(list(events))
                    if got != want or ref != want:
                        gok = False
                        bad.append((events[:3], want[:3], got[:3]))
                except Exception as exc:  # noqa: BLE001
                    gok = False
                    bad.append((events[:3], want[:3], f"raised {type(exc).__name__}"))
            grp(name, gok, "" if gok else str(bad[0])[:220])

    score = sum(w for name, w, _ in GROUPS
                if any(line.startswith("OK") and name in line for line, _ in results))
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
