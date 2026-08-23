"""Deterministic generators for avo-lab eval inputs.

Run from repo root:  python avo-lab/tools/gen_inputs.py
Regenerating overwrites task inputs with identical content (fixed seeds).
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
TASKS = LAB / "evals" / "tasks"

LEVELS = ["INFO", "INFO", "INFO", "WARN", "ERROR"]
MSGS = {
    "INFO": [
        "request served path=/api/users status=200",
        "cache hit key=session:{n}",
        "worker heartbeat id={n}",
        "request served path=/api/orders status=200",
        "snapshot saved shard={n}",
    ],
    "WARN": [
        "slow query ms={n} table=orders",
        "retry scheduled attempt={n}",
        "degraded pool size={n}",
        "message contained literal ERROR token but level is WARN id={n}",
        "queue depth={n}",
    ],
    "ERROR": [
        "payment declined order={n}",
        "db connection lost attempt={n}",
        "unhandled exception type=Timeout order={n}",
        "auth failed user={n}",
        "write failed shard={n}",
    ],
}


def gen_log(path: Path) -> None:
    rng = random.Random(42)
    t0 = datetime(2026, 8, 21, 8, 0, 0)
    lines = []
    for i in range(140):
        ts = t0 + timedelta(seconds=i * 7 + rng.randint(0, 3))
        level = rng.choice(LEVELS)
        msg = rng.choice(MSGS[level]).format(n=rng.randint(1, 999))
        lines.append(f"{ts.strftime('%Y-%m-%dT%H:%M:%SZ')} {level} {msg}")
    # inject duplicate-timestamp pairs (tests stable-sort tie rule)
    lines[50] = lines[49].replace(" WARN ", " ERROR ") if " WARN " in lines[49] else lines[50]
    dup = lines[80]
    lines.insert(81, dup)
    # decoy: INFO line whose message mentions ERROR
    lines.insert(
        100,
        f"{t0.isoformat()}Z INFO parsed legacy record containing token ERROR id=7",
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def gen_csv(path: Path) -> None:
    rng = random.Random(1337)
    regions = ["north", "south", "east", "west"]
    products = ["chair", "desk", "lamp", "shelf"]
    rows = []
    for i in range(48):
        rows.append(
            {
                "order_id": 1000 + i,
                "region": rng.choice(regions),
                "product": rng.choice(products),
                "quantity": rng.randint(1, 12),
                # 3-decimal prices force a real rounding decision
                "unit_price": f"{rng.uniform(3, 90):.3f}",
            }
        )
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["order_id", "region", "product", "quantity", "unit_price"])
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    gen_log(TASKS / "e1-log-triage" / "app.log")
    gen_csv(TASKS / "e2-csv-stats" / "sales.csv")
    print("inputs regenerated")
