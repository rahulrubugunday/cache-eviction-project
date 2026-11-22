from collections import OrderedDict, defaultdict
from .entry import Entry


class LFUCache:
    def __init__(self, capacity, ttl=None):
        self.capacity = capacity
        self.ttl = ttl
        self.index = {}
        self.counts = {}
        self.buckets = defaultdict(OrderedDict)
        self.min_count = 0

    def _bump(self, key):
        count = self.counts[key]
        del self.buckets[count][key]
        if not self.buckets[count]:
            del self.buckets[count]
            if self.min_count == count:
                self.min_count += 1
        self.counts[key] = count + 1
        self.buckets[count + 1][key] = None

    def _delete(self, key):
        count = self.counts.pop(key)
        del self.buckets[count][key]
        if not self.buckets[count]:
            del self.buckets[count]
        del self.index[key]

    def get(self, key):
        entry = self.index.get(key)
        if entry is None:
            return None
        if entry.is_expired():
            self._delete(key)
            return None
        self._bump(key)
        return entry.value

    def put(self, key, value):
        if self.capacity <= 0:
            return
        if key in self.index:
            self.index[key] = Entry(key, value, self.ttl)
            self._bump(key)
            return

        if len(self.index) >= self.capacity:
            if self.min_count not in self.buckets:
                self.min_count = min(self.buckets)
            victim, _ = self.buckets[self.min_count].popitem(last=False)
            if not self.buckets[self.min_count]:
                del self.buckets[self.min_count]
            del self.index[victim]
            del self.counts[victim]

        self.index[key] = Entry(key, value, self.ttl)
        self.counts[key] = 1
        self.buckets[1][key] = None
        self.min_count = 1

    def __len__(self):
        return len(self.index)