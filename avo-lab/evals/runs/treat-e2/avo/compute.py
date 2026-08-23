import csv
import json
from decimal import Decimal, ROUND_HALF_UP

REGIONS = ["north", "south", "east", "west"]

revenue = {r: Decimal("0") for r in REGIONS}
grand = Decimal("0")
qty_by_product = {}
total_orders = 0

with open("sales.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        total_orders += 1
        line_total = Decimal(row["quantity"].strip()) * Decimal(row["unit_price"].strip())
        revenue[row["region"].strip()] += line_total
        grand += line_total
        p = row["product"].strip()
        qty_by_product[p] = qty_by_product.get(p, 0) + int(row["quantity"])

top_product = sorted(qty_by_product.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

def money(d):
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

parts = []
for r in REGIONS:
    parts.append(f'"{r}": {money(revenue[r])}')
text = (
    "{\n"
    f'  "total_orders": {total_orders},\n'
    f'  "revenue_by_region": {{{", ".join(parts)}}},\n'
    f'  "top_product": {json.dumps(top_product)},\n'
    f'  "grand_total": {money(grand)}\n'
    "}\n"
)

parsed = json.loads(text)
assert set(parsed) == {"total_orders", "revenue_by_region", "top_product", "grand_total"}
with open("stats.json", "w", encoding="utf-8") as out:
    out.write(text)
print(text)
print("products:", qty_by_product)
