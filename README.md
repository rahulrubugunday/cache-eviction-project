# Cache Eviction Project

A Python project that builds three cache eviction policies from scratch and tests them in three ways: against synthetic traffic, against a real Twitter trace, and behind a small web service under load.

## What is in this project

**1. Three caches**

| Policy | When the cache is full, it removes... |
|---|---|
| FIFO (First In, First Out) | the item that was added first |
| LRU (Least Recently Used) | the item that has not been used for the longest time |
| LFU (Least Frequently Used) | the item that has been used the fewest times (ties go to the least recently used) |

Every cache supports an optional TTL, which is the number of seconds an item may live before it expires.

**2. A benchmark**

Replays request streams through each cache and measures hit rate, lookup time and memory per item. The streams are:
- random traffic
- Zipf traffic (a few keys are very popular) where the favorites never change
- Zipf traffic where the favorites change 4 or 20 times
- a real Twitter trace of 1,000,000 requests

**3. A cache stampede demo**

50 threads ask for the same item against a slow database (each query takes 100 ms). When the cached item expires, they all go to the database at once. The demo compares no protection with a lock that lets only one thread fetch.

**4. A web service and load test**

A FastAPI service with an LRU cache in front of the slow database. It has two endpoints, one without stampede protection and one with a per-key lock. Locust sends 50 simulated users at each one.

## Setup

You need Python 3.10 or newer.

```
pip install fastapi uvicorn locust pytest
```

### The Twitter trace

The Twitter trace is about 36 MB, so it is not stored in this repository. Download the Twitter cluster 52 trace from the [libCacheSim](https://github.com/1a1a11a/libCacheSim) project, convert it to a CSV file, and save it as:

```
traces/twitter_cluster52.csv
```

The first line of the file is a header, and each following line holds `time, object, size, next_access_vtime`. The loader in `workloads.py` reads the second column (`object`) as the cache key.

Without this file, Part 2 of the benchmark cannot run. Everything else works without it.

## How to run

### Unit tests
```
python -m pytest tests -v
```

### Benchmark and stampede demo
```
python main.py
```
This runs the benchmark and then the stampede demo. It takes a few minutes, because the Twitter trace is replayed several times.

### Web service and load test

Use two terminals. In the first, start the server:
```
python -m uvicorn app:app --port 8000
```

In the second, start Locust:
```
python -m locust -f locustfile.py --host http://localhost:8000
```
Locust runs two kinds of users at the same time and splits the users between them:
- `ShopUser` requests `/items/{id}`, which has no stampede protection.
- `LockedShopUser` requests `/items-locked/{id}`, which has the per-key lock.

Open http://localhost:8089, enter 100 users and a spawn rate of 50 (about 50 users for each endpoint), and press Start. Stop it after about 30 seconds. Then open http://localhost:8000/stats to read the database counters for both endpoints.

Restart the server before each new test so the counters start from zero. Run only one server worker, because `app.py` recreates the database when it starts.

## Results

### Benchmark: Twitter trace, 1,000-item cache

| Policy | Hit rate |
|---|---|
| FIFO | 61.4% |
| LRU | 64.1% |
| LFU | 51.3% |

LRU gives the best hit rate on this trace. LFU is the worst here, and it also struggles when the popular keys keep changing, because items that were popular in the past keep their high use counts.

### Stampede demo: 50 users, 3 seconds, one hot item

| Mode | Database queries | Most queries at once |
|---|---|---|
| No protection | 150 | 50 |
| Lock | 3 | 1 |

### Load test: 50 users, about 30 seconds each

| | No protection | With the lock |
|---|---|---|
| Requests | 20,915 | 20,592 |
| Failures | 0 | 0 |
| Database queries | 4,521 | 3,706 |
| Most queries at once | 40 | 29 |
| Median response time | 13 ms | 15 ms |

The lock reduces the work done by the database by about 18%, but it does not make responses faster. The lock is per key, so requests for different missing items can still query the database at the same time.

Numbers vary a little from run to run, especially timings.
