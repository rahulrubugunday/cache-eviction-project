import threading
from fastapi import FastAPI, HTTPException
from caches import LRUCache
from db import Database, setup_db

app = FastAPI()

cache = LRUCache(100, ttl=1.0)
cache_lock = threading.Lock()
db = Database()
setup_db()


@app.get("/items/{item_id}")
def get_item(item_id: str):
    with cache_lock:
        value = cache.get(item_id)
    if value is not None:
        return {"id": item_id, "name": value, "source": "cache"}

    try:
        value = db.fetch(item_id)
    except TypeError:
        raise HTTPException(status_code=404, detail="item not found")

    with cache_lock:
        cache.put(item_id, value)
    return {"id": item_id, "name": value, "source": "db"}


@app.get("/stats")
def stats():
    return {"db_queries": db.queries, "db_peak": db.peak, "cached_items": len(cache)}


locked_cache = LRUCache(100, ttl=1.0)
locked_db = Database()
key_locks = {}
key_locks_guard = threading.Lock()


def get_key_lock(key):
    with key_locks_guard:
        if key not in key_locks:
            key_locks[key] = threading.Lock()
        return key_locks[key]


@app.get("/items-locked/{item_id}")
def get_item_locked(item_id: str):
    with cache_lock:
        value = locked_cache.get(item_id)
    if value is not None:
        return {"id": item_id, "name": value, "source": "cache"}

    with get_key_lock(item_id):
        with cache_lock:
            value = locked_cache.get(item_id)
        if value is not None:
            return {"id": item_id, "name": value, "source": "cache"}

        try:
            value = locked_db.fetch(item_id)
        except TypeError:
            raise HTTPException(status_code=404, detail="item not found")

        with cache_lock:
            locked_cache.put(item_id, value)
    return {"id": item_id, "name": value, "source": "db"}


@app.get("/stats-locked")
def stats_locked():
    return {"db_queries": locked_db.queries, "db_peak": locked_db.peak, "cached_items": len(locked_cache)}