from collections import OrderedDict
from .entry import Entry


class FIFOCache:
    def __init__(self, capacity, ttl=None):
        self.capacity = capacity
        self.ttl = ttl
        self.items = OrderedDict()

    def get(self, key):
        entry = self.items.get(key)
        if entry is None:
            return None
        if entry.is_expired():
            del self.items[key]
            return None
        return entry.value

    def put(self, key, value):
        if key in self.items:
            self.items[key] = Entry(key, value, self.ttl)
            return
        if len(self.items) >= self.capacity:
            self.items.popitem(last=False)
        self.items[key] = Entry(key, value, self.ttl)

    def __len__(self):
        return len(self.items)