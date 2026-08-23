def is_balanced(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    openers = {"(", "[", "{"}
    stack = []
    in_quote = ""
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if in_quote:
            if c == "\\":
                i += 2
                continue
            if c == in_quote:
                in_quote = ""
            i += 1
            continue
        if c == "\\":
            i += 2
            continue
        if c == "'" or c == '"':
            in_quote = c
            i += 1
            continue
        if c in openers:
            stack.append(c)
        elif c in pairs:
            if not stack or stack[-1] != pairs[c]:
                return False
            stack.pop()
        i += 1
    return not stack
