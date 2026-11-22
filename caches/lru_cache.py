from .entry import Entry


class Node(Entry):
    def __init__(self, key=None, value=None, ttl=None):
        super().__init__(key, value, ttl)
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity, ttl=None):
        self.capacity = capacity
        self.ttl = ttl
        self.index = {}

        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        first = self.head.next
        node.prev = self.head
        node.next = first
        self.head.next = node
        first.prev = node

    def get(self, key):
        node = self.index.get(key)
        if node is None:
            return None
        if node.is_expired():
            self._remove(node)
            del self.index[key]
            return None
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key, value):
        if key in self.index:
            self._remove(self.index[key])
        node = Node(key, value, self.ttl)
        self.index[key] = node
        self._add_to_front(node)

        if len(self.index) > self.capacity:
            oldest = self.tail.prev
            self._remove(oldest)
            del self.index[oldest.key]

    def __len__(self):
        return len(self.index)