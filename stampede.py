import threading
import time
from caches import LRUCache
from db import Database, setup_db

USERS = 50
DURATION = 3
TTL = 1.0
KEY = "item0"
SLOW = 0.05

fetch_lock = threading.Lock()


class SafeCache:
    def __init__(self, cache):
        self.cache = cache
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            return self.cache.get(key)

    def put(self, key, value):
        with self.lock:
            self.cache.put(key, value)


def no_protection(cache, db):
    value = cache.get(KEY)
    if value is None:
        value = db.fetch(KEY)
        cache.put(KEY, value)
    return value


def with_lock(cache, db):
    value = cache.get(KEY)
    if value is None:
        with fetch_lock:
            value = cache.get(KEY)
            if value is None:
                value = db.fetch(KEY)
                cache.put(KEY, value)
    return value


def run(mode):
    cache = SafeCache(LRUCache(100, ttl=TTL))
    db = Database()
    results = {"requests": 0, "slow": 0}
    results_lock = threading.Lock()
    stop_time = time.time() + DURATION

    def user():
        while time.time() < stop_time:
            start = time.time()
            mode(cache, db)
            took = time.time() - start

            with results_lock:
                results["requests"] += 1
                if took > SLOW:
                    results["slow"] += 1
            time.sleep(0.01)

    threads = []
    for _ in range(USERS):
        t = threading.Thread(target=user)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    return results["requests"], db.queries, db.peak, results["slow"]


def run_stampede():
    setup_db()
    print(f"{USERS} users, {DURATION}s, items stay fresh for {TTL}s, each database query takes 100 ms\n")
    print("mode            requests  DB queries  peak at once  slow")

    for name, mode in [("no protection", no_protection), ("lock", with_lock)]:
        requests, queries, peak, slow = run(mode)
        print(f"{name:<15} {requests:8} {queries:11} {peak:13} {slow:5}")


if __name__ == "__main__":
    run_stampede()
