def is_balanced(s: str) -> bool:
    stack = []
    escaped = False
    quote = None  # None, "'" or '"'
    for ch in s:
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if quote is not None:
            if ch == quote:
                quote = None
            continue
        if ch == "'" or ch == '"':
            quote = ch
        elif ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != {")": "(", "]": "[", "}": "{"}[ch]:
                return False
            stack.pop()
    return len(stack) == 0
