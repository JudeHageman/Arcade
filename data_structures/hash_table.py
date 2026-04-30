"""
HashTable implementation in Python.
Author: Jude Hageman
Date: 4/24/2026

This file contains the implementation of a the hashtable data structure.
"""
from dynamic_array import ArrayList

class HashTable:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.size = 0
        # Create an ArrayList of ArrayLists for chaining
        self.table = ArrayList(capacity)
        for _ in range(capacity):
            self.table.append(ArrayList())

    def _hash(self, key):
        return hash(key) % self.capacity

    def _resize(self):
        old_table = self.table
        old_capacity = self.capacity
        self.capacity = self.capacity * 2
        self.table = ArrayList(self.capacity)
        for _ in range(self.capacity):
            self.table.append(ArrayList())
        self.size = 0
        for i in range(old_capacity):
            for key, value in old_table[i]:
                self.put(key, value)

    def put(self, key, value):
        if self.size >= self.capacity * 0.75:
            self._resize()
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

    def remove(self, key):
        index = self._hash(key)
        bucket = self.table[index]
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                bucket.pop(i)
                self.size -= 1
                return
        raise KeyError(key)

    def __contains__(self, key):
        index = self._hash(key)
        bucket = self.table[index]
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                return True
        return False

    def clear(self):
        for i in range(self.capacity):
            self.table[i] = ArrayList()
        self.size = 0