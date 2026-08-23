"""Visible symptom demo. Passing this is necessary, not sufficient."""
from warehouse import Inventory

inv = Inventory()
inv.receive("bolt", 10)
rid = inv.reserve("bolt", 6)
print("available after reserving 6 of 10:", inv.available("bolt"))
try:
    inv.reserve("bolt", 5)  # only 4 available -> must raise
    print("BUG: oversell allowed")
except ValueError:
    print("ok: oversell blocked")
inv.release("bolt", rid, 2)
print("available after partial release:", inv.available("bolt"), "(expect 6)")
