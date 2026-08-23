"""Zigbus wire-event interpreter.

Interprets Zigbus wire events (strings) in order and returns the exact
transcript as a list of output lines. Pure standard library.
"""

_DIGITS = set("0123456789")


def _is_valid_key(k):
    # Exactly 4 chars, each in 0-9 A-F, uppercase only.
    if not isinstance(k, str) or len(k) != 4:
        return False
    for ch in k:
        if not (("0" <= ch <= "9") or ("A" <= ch <= "F")):
            return False
    return True


def _is_valid_n(n_tok):
    # Decimal integer token: digits only (no sign), parses >= 0.
    if not isinstance(n_tok, str) or n_tok == "":
        return False
    for ch in n_tok:
        if ch not in _DIGITS:
            return False
    return True


def run(events: list[str]) -> list[str]:
    out: list[str] = []
    state = "DOWN"
    seq = 0
    oflow = 0
    key = None

    for event in events:
        tokens = event.split(" ")
        first = tokens[0] if tokens else ""

        if first == "OPEN":
            k = tokens[1] if len(tokens) > 1 else None
            if not _is_valid_key(k):
                out.append("ERR BAD-KEY")
            elif state != "DOWN":
                out.append("ERR BUSY")
            else:
                state = "UP"
                seq = 0
                oflow = 0
                key = k
                out.append("WELCOME")

        elif first == "SEND":
            n_tok = tokens[1] if len(tokens) > 1 else None
            if not _is_valid_n(n_tok):
                out.append("ERR BAD-N")
            elif state == "UP":
                n = int(n_tok)
                total = seq + n
                new = total % 65536
                if total >= 65536:
                    oflow = 1
                seq = new
                if oflow == 1:
                    out.append("NAK OFLOW")
                else:
                    out.append(f"ACK {seq}")
            elif state == "WAIT":
                out.append("DEFERRED")
            else:  # DOWN
                out.append("ERR CLOSED")

        elif first == "PARK":
            if state == "DOWN":
                out.append("ERR CLOSED")
            else:
                state = "WAIT"
                out.append("PARKED")

        elif first == "RESUME":
            k = tokens[1] if len(tokens) > 1 else None
            if not _is_valid_key(k):
                out.append("ERR BAD-KEY")
            elif state == "DOWN":
                out.append("ERR CLOSED")
            elif state == "UP":
                out.append("ERR ACTIVE")
            elif k == key:
                state = "UP"
                out.append("RESUMED")
            else:
                out.append("ERR BAD-KEY")

        elif first == "RESET":
            state = "DOWN"
            seq = 0
            oflow = 0
            key = None
            out.append("RESET-OK")

        elif first == "CLOSE":
            if state == "DOWN":
                pass  # Emit NOTHING for this event.
            else:
                state = "DOWN"  # key, seq, oflow are NOT cleared here.
                out.append("BYE")

        else:
            out.append("ERR UNKNOWN")

    out.append(f"SEQ {seq} OFLOW {oflow}")
    return out
