"""E1 checker — log triage. Usage: python e1_checker.py <task_dir>"""
import sys
from pathlib import Path


def expected(task: Path):
    lines = (task / "app.log").read_text(encoding="utf-8").splitlines()
    err = [ln for ln in lines if len(ln.split()) >= 2 and ln.split()[1] == "ERROR"]
    return sorted(err, key=lambda ln: ln.split()[0])  # stable sort


def main():
    task = Path(sys.argv[1])
    exp = expected(task)
    out_path = task / "errors.txt"
    results = []

    def grp(name, ok, detail=""):
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    if not out_path.exists():
        grp("file-exists", False, "errors.txt missing")
        grp("line-set", False)
        grp("exact-match", False)
    else:
        got = out_path.read_text(encoding="utf-8")
        got_lines = got.splitlines()
        grp("file-exists", True, f"{len(got_lines)} lines")

        def key(ln):
            parts = ln.split()
            return parts[0] if len(parts) >= 2 else ""

        got_err = [ln for ln in got_lines if len(ln.split()) >= 2 and ln.split()[1] == "ERROR"]
        grp("line-set", sorted(got_lines, key=key) == exp,
            f"expected {len(exp)} error lines, got {len(got_lines)} lines")
        grp("exact-match", got == "\n".join(exp) + ("\n" if exp else ""),
            "verbatim content, stable order, single trailing newline")

    score = sum(w for (_, ok), w in zip(results, (20, 40, 40)) if ok)
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
