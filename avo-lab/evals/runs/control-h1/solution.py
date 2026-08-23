from collections import OrderedDict


class TTLCache:
    def __init__(self, capacity: int, clock):
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be an int >= 1")
        self._capacity = capacity
        self._clock = clock
        self._entries = OrderedDict()

    @staticmethod
    def _expired(expires_at, now) -> bool:
        return expires_at is not None and now >= expires_at

    def put(self, key, value, ttl=None) -> None:
        now = self._clock()
        entry = self._entries.get(key)
        if entry is not None and self._expired(entry[1], now):
            del self._entries[key]
            entry = None
        if entry is None and len(self._entries) >= self._capacity:
            self._entries.popitem(last=False)
        self._entries[key] = [value, None if ttl is None else now + ttl]
        self._entries.move_to_end(key)

    def get(self, key, default=None):
        entry = self._entries.get(key)
        if entry is None:
            return default
        now = self._clock()
        if self._expired(entry[1], now):
            del self._entries[key]
            return default
        self._entries.move_to_end(key)
        return entry[0]

    def delete(self, key) -> bool:
        entry = self._entries.get(key)
        if entry is None:
            return False
        if self._expired(entry[1], self._clock()):
            del self._entries[key]
            return False
        del self._entries[key]
        return True

    def clear(self) -> int:
        removed = len(self._entries)
        self._entries.clear()
        return removed
