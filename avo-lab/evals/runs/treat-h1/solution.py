"""TTL + LRU cache: O(1) average get/put/delete via dict + doubly-linked list.

Recency is the node's position in the list (MRU next to head sentinel), so
LRU order never depends on distinct clock readings. Expiry is stored as an
absolute deadline; an entry is expired iff the deadline is set and
now >= deadline (boundary exclusive on validity).
"""


class _Node:
    __slots__ = ("key", "value", "expires_at", "prev", "next")

    def __init__(self, key=None, value=None, expires_at=None):
        self.key = key
        self.value = value
        self.expires_at = expires_at
        self.prev = None
        self.next = None


class TTLCache:
    def __init__(self, capacity, clock):
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be an int >= 1")
        self._capacity = capacity
        self._clock = clock
        self._map = {}
        self._head = _Node()
        self._tail = _Node()
        self._head.next = self._tail
        self._tail.prev = self._head

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _link_front(self, node):
        first = self._head.next
        node.prev = self._head
        node.next = first
        self._head.next = node
        first.prev = node

    def _remove(self, node):
        self._unlink(node)
        del self._map[node.key]

    def _expired(self, node, now):
        return node.expires_at is not None and now >= node.expires_at

    def put(self, key, value, ttl=None):
        now = self._clock()
        node = self._map.get(key)
        if node is not None and self._expired(node, now):
            self._remove(node)
            node = None
        if node is not None:
            node.value = value
            node.expires_at = None if ttl is None else now + ttl
            self._unlink(node)
            self._link_front(node)
            return
        if len(self._map) >= self._capacity:
            self._remove(self._tail.prev)
        node = _Node(key, value, None if ttl is None else now + ttl)
        self._map[key] = node
        self._link_front(node)

    def get(self, key, default=None):
        now = self._clock()
        node = self._map.get(key)
        if node is None:
            return default
        if self._expired(node, now):
            self._remove(node)
            return default
        self._unlink(node)
        self._link_front(node)
        return node.value

    def delete(self, key):
        now = self._clock()
        node = self._map.get(key)
        if node is None:
            return False
        expired = self._expired(node, now)
        self._remove(node)
        return not expired

    def clear(self):
        count = len(self._map)
        self._map.clear()
        self._head.next = self._tail
        self._tail.prev = self._head
        return count
