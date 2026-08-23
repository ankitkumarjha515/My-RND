import csv
import json
from decimal import Decimal, ROUND_HALF_UP

REGIONS = ["north", "south", "east", "west"]

revenue_by_region = {r: Decimal("0") for r in REGIONS}
grand_total = Decimal("0")
total_orders = 0
qty_by_product = {}

with open("sales.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        qty = int(row["quantity"])
        price = Decimal(row["unit_price"])
        line_total = qty * price
        region = row["region"]
        if region not in revenue_by_region:
            raise ValueError(f"unexpected region: {region!r}")
        revenue_by_region[region] += line_total
        grand_total += line_total
        qty_by_product[row["product"]] = qty_by_product.get(row["product"], 0) + qty
        total_orders += 1

def q2(d: Decimal) -> float:
    return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

top_product = sorted(qty_by_product.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

stats = {
    "total_orders": total_orders,
    "revenue_by_region": {r: q2(revenue_by_region[r]) for r in REGIONS},
    "top_product": top_product,
    "grand_total": q2(grand_total),
}

with open("stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)
    f.write("\n")

print(json.dumps(stats, indent=2))
