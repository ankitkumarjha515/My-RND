"""X4 checker - corpus statistics. Usage: python x4_checker.py <task_dir>"""
import json
import re
import sys
from pathlib import Path


def expected(task: Path):
    text = (task / "corpus.txt").read_text(encoding="utf-8")
    s1 = len(text.replace("\n", ""))
    s2 = sum(1 for i, ch in enumerate(text)
             if ch == "q" and (i + 1 >= len(text) or text[i + 1] != "u"))
    words = re.findall(r"[A-Za-z]+", text)
    s3 = sum(1 for w in words
             if any(w[i].lower() == w[i + 1].lower() for i in range(len(w) - 1)))
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    s4 = sum(1 for ln in lines if any(c.isdigit() for c in ln))
    nums = [int(n) for n in re.findall(r"[0-9]+", text)]
    s5 = sum(nums) % 1000003
    return {"chars_no_newlines": s1, "q_not_followed_by_u": s2,
            "words_with_doubled_letters": s3, "lines_with_digits": s4,
            "integer_tokens_sum_mod": s5}


def main():
    task = Path(sys.argv[1])
    results = []

    def grp(name, ok, detail=""):
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    try:
        exp = expected(task)
    except (FileNotFoundError, OSError) as exc:
        exp = None
        grp("corpus-present", False, f"missing input: {exc}")
    except Exception as exc:  # noqa: BLE001
        exp = None
        grp("corpus-present", False, f"{type(exc).__name__}: {exc}")

    if exp is not None:
        path = task / "counts.json"
        got = None
        try:
            got = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            grp("json-parses", False, str(exc)[:120])
        if isinstance(got, dict):
            grp("json-parses", True)
            for key in exp:
                grp(key, got.get(key) == exp[key], f"expected {exp[key]}")
        elif got is not None:
            grp("json-parses", True)
            for key in exp:
                grp(key, False, "not an object")
        if len(results) < 6 and "json-parses" not in [r[0][4:] for r in [(l,) for l, _ in results]]:
            for key in list(exp)[max(0, len(results) - 1):]:
                grp(key, False)

    weights = {"corpus-present": 0, "json-parses": 10,
               "chars_no_newlines": 18, "q_not_followed_by_u": 18,
               "words_with_doubled_letters": 18, "lines_with_digits": 18,
               "integer_tokens_sum_mod": 18}
    score = sum(w for name, w in weights.items()
                if any(line.startswith("OK") and name in line for line, _ in results))
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if exp is not None and all(ok for _, ok in results) and score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
