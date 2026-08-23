"""Warehouse inventory ledger.

Behavioral spec lives in README.md and is authoritative.
"""

class Inventory:
    def __init__(self):
        self._stock = {}         # sku -> on-hand units
        self._reservations = {}  # sku -> list of [rid, qty] live entries (FIFO order)
        self._next_rid = {}      # sku -> next reservation id to hand out

    def _require(self, sku, qty):
        if not isinstance(sku, str) or sku == "":
            raise ValueError("bad sku")
        if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
            raise ValueError("bad qty")
        if sku not in self._stock:
            raise ValueError("unknown sku")

    def receive(self, sku, qty):
        if not isinstance(sku, str) or sku == "":
            raise ValueError("bad sku")
        if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
            raise ValueError("bad qty")
        self._stock[sku] = self._stock.get(sku, 0) + qty
        self._reservations.setdefault(sku, [])
        self._next_rid.setdefault(sku, 1)

    def reserve(self, sku, qty):
        self._require(sku, qty)
        # Guard against *available* units (on-hand minus live reservations),
        # not raw stock, else existing reservations can be oversold.
        if qty > self.available(sku):
            raise ValueError("insufficient")
        rid = self._next_rid[sku]
        self._next_rid[sku] += 1
        self._reservations[sku].append([rid, qty])
        return rid

    def release(self, sku, rid, qty):
        self._require(sku, qty)
        entries = self._reservations[sku]
        for i, entry in enumerate(entries):
            if entry[0] == rid:
                # Shrink by at most the reservation's remaining size.
                take = min(qty, entry[1])
                entry[1] -= take
                if entry[1] == 0:
                    entries.pop(i)
                return
        raise ValueError("unknown rid")

    def commit(self, sku, qty):
        self._require(sku, qty)
        if qty > self._stock[sku]:
            raise ValueError("insufficient stock")
        self._stock[sku] -= qty
        # Consume LIVE reservations oldest-first (FIFO) up to qty units;
        # any shortfall simply comes off stock.
        remaining = qty
        entries = self._reservations[sku]
        while remaining > 0 and entries:
            entry = entries[0]
            take = min(remaining, entry[1])
            entry[1] -= take
            remaining -= take
            if entry[1] == 0:
                entries.pop(0)

    def available(self, sku):
        # Query-only: unknown/invalid skus simply have nothing available.
        if not isinstance(sku, str) or sku == "" or sku not in self._stock:
            return 0
        reserved_total = sum(entry[1] for entry in self._reservations.get(sku, []))
        return max(0, self._stock[sku] - reserved_total)
