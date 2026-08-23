"""Warehouse inventory ledger.

NOTE: this implementation is known to misbehave in scenarios beyond the
basic demo. The behavioral spec lives in README.md and is authoritative.
"""


class Inventory:
    def __init__(self):
        self._stock = {}         # sku -> on-hand units
        self._reserved = {}      # sku -> total reserved units
        self._reservations = {}  # sku -> list of [rid, qty]
        self._next_rid = {}

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
        self._reserved.setdefault(sku, 0)
        self._reservations.setdefault(sku, [])
        self._next_rid.setdefault(sku, 1)

    def reserve(self, sku, qty):
        # TODO: guard looks suspicious vs reservations
        self._require(sku, qty)
        if qty > self._stock[sku]:
            raise ValueError("insufficient")
        rid = self._next_rid[sku]
        self._next_rid[sku] += 1
        self._reservations[sku].append([rid, qty])
        self._reserved[sku] += qty
        return rid

    def release(self, sku, rid, qty):
        self._require(sku, qty)
        for entry in self._reservations[sku]:
            if entry[0] == rid:
                # BUG: wipes the whole reservation regardless of qty
                self._reservations[sku].remove(entry)
                self._reserved[sku] -= entry[1]
                return
        raise ValueError("unknown rid")

    def commit(self, sku, qty):
        self._require(sku, qty)
        if qty > self._stock[sku]:
            raise ValueError("insufficient stock")
        self._stock[sku] -= qty
        # BUG: reserved total shrinks but the live reservation entries are
        # never consumed FIFO, so availability goes stale.
        take = min(qty, self._reserved[sku])
        self._reserved[sku] -= take

    def available(self, sku):
        if not isinstance(sku, str) or sku == "" or sku not in self._stock:
            return 0
        return max(0, self._stock[sku] - self._reserved.get(sku, 0))
