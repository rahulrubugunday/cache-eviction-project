import time
import tracemalloc
from collections import Counter
from caches import FIFOCache, LRUCache, LFUCache
from workloads import random_requests, zipf_requests, shifting_zipf_requests, load_trace

POLICIES = {"FIFO": FIFOCache, "LRU": LRUCache, "LFU": LFUCache}
SIZES = [10, 50, 100, 500]


def replay(cache, requests):
    hits = 0
    total_ns = 0
    for key in requests:
        start = time.perf_counter_ns()
        value = cache.get(key)
        total_ns += time.perf_counter_ns() - start

        if value is not None:
            hits += 1
        else:
            cache.put(key, "data")

    hit_rate = hits / len(requests)
    avg_ns = total_ns / len(requests)
    return hit_rate, avg_ns


def memory_used(cache_class, size, requests):
    tracemalloc.start()
    before = tracemalloc.get_traced_memory()[0]

    cache = cache_class(size)
    for key in requests:
        if cache.get(key) is None:
            cache.put(key, "data")

    after = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return after - before


def compare(title, requests):
    print("\n" + title)
    print("size   FIFO     LRU     LFU")
    for size in SIZES:
        line = f"{size:<6}"
        for name in POLICIES:
            hit_rate, _ = replay(POLICIES[name](size), requests)
            line += f"{hit_rate:7.1%} "
        print(line)


def full_report(title, requests, sizes):
    print("\n" + title)
    for size in sizes:
        print(f"\ncache size {size}")
        print("policy  hit rate  lookup(ns)  memory(MB)  bytes/item")
        for name in POLICIES:
            hit_rate, avg_ns = replay(POLICIES[name](size), requests)
            memory = memory_used(POLICIES[name], size, requests)
            print(f"{name:<7} {hit_rate:8.1%} {avg_ns:11.0f} {memory / 1e6:11.1f} {memory / size:11.0f}")


# def describe(keys):
#     counts = Counter(keys)
#     print("total requests:", len(keys))
#     print("different keys:", len(counts))

#     once = 0
#     for count in counts.values():
#         if count == 1:
#             once += 1
#     print(f"keys asked for only once: {once} ({once / len(counts):.0%})")

#     for n in [10, 100, 1000, 10000]:
#         top_total = 0
#         for _, count in counts.most_common(n):
#             top_total += count
#         print(f"top {n} keys got {top_total / len(keys):.0%} of requests")


def run_benchmark():
    print("PART 1: Synthetic traffic (hit rate)")
    compare("Random (1,000 keys, 100,000 requests)", random_requests(1000, 100000))
    compare("Zipf, favorites never change", zipf_requests(1000, 100000))
    compare("Zipf, favorites change 4 times", shifting_zipf_requests(1000, 100000, phases=4))
    compare("Zipf, favorites change 20 times", shifting_zipf_requests(1000, 100000, phases=20))

    print("\nPART 2: Twitter trace")
    keys = load_trace("traces/twitter_cluster52.csv")
    # describe(keys)
    full_report("Twitter trace (1,000,000 requests)", keys, [1000, 10000, 50000])


if __name__ == "__main__":
    run_benchmark()
