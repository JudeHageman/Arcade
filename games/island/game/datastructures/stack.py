"""
stack.py - Stack implementation using a custom ArrayList.

This module provides a LIFO (Last-In, First-Out) data structure 
required for the Time Travel system in Lab 4.
"""

from .arraylist import ArrayList 

class Stack:
    def __init__(self):
        """Initialize an empty stack using the custom ArrayList."""
        self._data = ArrayList()

    def push(self, item):
        """
        Add an item to the top of the stack.
        
        Args:
            item: The element to be added.
        """
        self._data.append(item)

    def pop(self):
        """
        Remove and return the top item from the stack.
        
        Returns:
            The top item if the stack is not empty, otherwise None.
        """
        if self.is_empty():
            return None
        # Uses the pop() method from ArrayList at the last index
        return self._data.pop(self._data.size - 1)

    def peek(self):
        """
        Return the top item without removing it.
        
        Returns:
            The top item if the stack is not empty, otherwise None.
        """
        if self.is_empty():
            return None
        # Accesses the last element using __getitem__ indexing []
        return self._data[self._data.size - 1]

    def is_empty(self):
        """
        Check if the stack is empty.
        
        Returns:
            True if empty, False otherwise.
        """
        return self._data.size == 0

    def size(self):
        """
        Return the number of items in the stack.
        
        Returns:
            The current size of the stack.
        """
        return self._data.size

    def clear(self):
        """Remove all items from the stack."""
        self._data.clear()

    def __str__(self):
        """Return a string representation of the stack."""
        return str(self._data)