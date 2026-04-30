"""
hash_table.py - Hash Table implementation

Only required if you implement SparseMatrix using DOK (Option A).

Author: Minju Seo
Date:   2026-04-09
Lab:    Lab 6 - Sparse World Map
"""
"""
hash_table.py - Hash Table implementation
Custom implementation without using Python's built-in dict, set, or hash().
"""

from google.auth import default


class HashTable:

    def __init__(self, initial_capacity=64):
        self.capacity = initial_capacity
        self.size = 0
        # Use a list as a fixed-size array for buckets
        self.table = [None] * self.capacity

    def _hash(self, key):
        """General-purpose hash function for strings, ints, or tuples."""
        h = 0
        
        # 1. 만약 키가 문자열인 경우 (node_id가 "greet"일 때)
        if isinstance(key, str):
            for char in key:
                h = (h * 31) + ord(char) # 각 문자의 ASCII 값을 누적
                
        # 2. 만약 키가 튜플인 경우 (Lab 6의 (row, col) 호환용)
        elif isinstance(key, (tuple, list)):
            row, col = key
            h = (row * 73856093) ^ (col * 19349663)
            
        # 3. 만약 키가 숫자인 경우
        else:
            h = key

        return abs(h) % self.capacity

    def set(self, key, value):
        """Insert or update a key-value pair."""
        # Check load factor and resize if necessary
        if (self.size / self.capacity) >= 0.7:
            self._resize()

        idx = self._hash(key)
        if self.table[idx] is None:
            # Create a new bucket (using a simple list for chaining)
            self.table[idx] = [[key, value]]
            self.size += 1
        else:
            # Search for the key in the bucket for update
            for item in self.table[idx]:
                if item[0] == key:
                    item[1] = value
                    return
            # If key not found, append to the bucket
            self.table[idx].append([key, value])
            self.size += 1

    def get(self, key, default=None):
        idx = self._hash(key)
        bucket = self.table[idx]
        if bucket:
            for k, v in bucket:
                if k == key:
                    return v
        # 여기서 중요! 
        # 만약 Graph.py에서 "노드가 없을 때 KeyError"가 나길 기대한다면 
        # default를 반환하는 대신 raise KeyError(key)를 해줘야 할 수도 있어.
        return default

    def delete(self, key):
        """Remove a key, raise KeyError if not present."""
        idx = self._hash(key)
        bucket = self.table[idx]
        if bucket is None:
            raise KeyError(key)
        
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                bucket.pop(i)
                self.size -= 1
                return
        raise KeyError(key)

    def __contains__(self, key):
        """Check if key exists in table."""
        return self.get(key) is not None

    def __len__(self):
        """Return number of entries."""
        return self.size

    def items(self):
        """Yield (key, value) pairs."""
        for bucket in self.table:
            if bucket:
                for key, value in bucket:
                    yield key, value

    def _resize(self):
        """Double the capacity and rehash all existing keys."""
        old_table = self.table
        self.capacity *= 2
        self.table = [None] * self.capacity
        self.size = 0 # Reset size as set() will increment it
        
        for bucket in old_table:
            if bucket:
                for key, value in bucket:
                    self.set(key, value)