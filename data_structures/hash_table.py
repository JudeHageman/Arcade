"""
HashTable implementation in Python.
Author: Jude Hageman
Date: 4/24/2026

This file contains the implementation of a the hashtable data structure.
"""
from dynamic_array import ArrayList

class HashTable:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.size = 0
        # Create an ArrayList of ArrayLists for chaining
        self.table = ArrayList(capacity)
        for _ in range(capacity):
            self.table.append(ArrayList())

    def _hash(self, key):
        return hash(key) % self.capacity

    def put(self, key, value):
        index = self._hash(key)
        bucket = self.table[index]
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1

    def get(self, key):
        index = self._hash(key)
        bucket = self.table[index]
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                return bucket[i][1]
        raise KeyError(key)