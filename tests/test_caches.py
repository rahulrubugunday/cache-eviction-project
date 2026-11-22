import time
from caches import FIFOCache, LRUCache, LFUCache


def test_fifo_evicts_first_in():
    c = FIFOCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")                
    c.put("c", 3)
    assert c.get("a") is None and c.get("b") == 2


def test_lru_evicts_least_recent():
    c = LRUCache(2)
    c.put("a", 1) 
    c.put("b", 2)
    c.get("a")                 
    c.put("c", 3)
    assert c.get("b") is None and c.get("a") == 1


def test_lfu_evicts_least_frequent():
    c = LFUCache(2)
    c.put("a", 1); c.put("b", 2)
    c.get("a"); c.get("a")
    c.put("c", 3)
    assert c.get("b") is None and c.get("a") == 1


def test_ttl_expires_in_all():
    for cls in (FIFOCache, LRUCache, LFUCache):
        c = cls(2, ttl=0.1)
        c.put("x", 1)
        assert c.get("x") == 1
        time.sleep(0.15)
        assert c.get("x") is None, cls.__name__


if __name__ == "__main__":
    test_fifo_evicts_first_in()
    test_lru_evicts_least_recent()
    test_lfu_evicts_least_frequent()
    test_ttl_expires_in_all()
    print("All tests passed")