import time
from collections import OrderedDict


class DataCache:
    def __init__(self, max_size=100, ttl=300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.cache.move_to_end(key)
                return data
            else:
                del self.cache[key]
        return None

    def set(self, key, data):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (data, time.time())
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def invalidate(self, key):
        self.cache.pop(key, None)

    def clear(self):
        self.cache.clear()
