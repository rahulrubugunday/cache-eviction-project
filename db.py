import sqlite3
import threading
import time

DB_FILE = "store.db"
DB_DELAY = 0.1


def setup_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DROP TABLE IF EXISTS products")
    conn.execute("CREATE TABLE products (id TEXT PRIMARY KEY, name TEXT)")
    conn.executemany("INSERT INTO products VALUES (?, ?)",
                     [(f"item{i}", f"Product number {i}") for i in range(1000)])
    conn.commit()
    conn.close()


class Database:

    def __init__(self):
        self.queries = 0
        self.running_now = 0
        self.peak = 0
        self._lock = threading.Lock()

    def fetch(self, key):
        with self._lock:
            self.queries += 1
            self.running_now += 1
            self.peak = max(self.peak, self.running_now)
        try:
            conn = sqlite3.connect(DB_FILE)
            time.sleep(DB_DELAY)
            row = conn.execute("SELECT name FROM products WHERE id = ?", (key,)).fetchone()
            conn.close()
            return row[0]
        finally:
            with self._lock:
                self.running_now -= 1