"""Shopping cart for the Reach-out demo store.

Behavioral spec lives in README.md next to this file.
"""


class Cart:
    COUPONS = {"SAVE10": 0.10, "SAVE25": 0.25}

    def __init__(self):
        # item_id -> {"qty": int, "unit_price": float}
        self._items = {}
        self._coupons = []  # discount fractions, one entry per apply_coupon call

    def add(self, item_id, qty, unit_price):
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError("qty must be a positive int")
        entry = self._items.get(item_id)
        if entry is None:
            self._items[item_id] = {"qty": qty, "unit_price": unit_price}
        else:
            entry["qty"] += qty
            entry["unit_price"] = unit_price

    def remove(self, item_id):
        if item_id not in self._items:
            raise KeyError(item_id)
        del self._items[item_id]

    def set_quantity(self, item_id, qty):
        if item_id not in self._items:
            raise KeyError(item_id)
        if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
            raise ValueError("qty must be >= 1")
        self._items[item_id]["qty"] = qty

    def apply_coupon(self, code):
        if code not in self.COUPONS:
            raise ValueError(f"unknown coupon: {code}")
        self._coupons.append(self.COUPONS[code])

    def total_units(self):
        return sum(e["qty"] for e in self._items.values())

    def total(self):
        """Final payable amount after coupons, bulk discount, rounding."""
        subtotal = sum(e["qty"] * e["unit_price"] for e in self._items.values())
        factor = 1.0
        for d in self._coupons:
            factor *= 1.0 - d
        if self.total_units() >= 10:
            factor *= 0.95
        raw = subtotal * factor
        return float(int(raw * 100 + 0.5)) / 100.0
