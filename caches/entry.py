import time


class Entry:
    def __init__(self, key, value, ttl=None):
        self.key = key
        self.value = value
        self.expires_at = time.monotonic() + ttl if ttl is not None else None

    def is_expired(self):
        return self.expires_at is not None and time.monotonic() > self.expires_at