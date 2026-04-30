"""
stack.py - Stack data structure implementation

A Last-In-First-Out (LIFO) data structure.
The last item added is the first item removed (like a stack of plates).

Author: Jude Hageman
Date: 2/16/2026
Lab: Lab 4 - Time Travel with Stacks
"""
from .array import ArrayList

class Stack:
    """
    A LIFO (Last-In-First-Out) data structure.
    
    The last item added is the first item removed.
    Think of it like a stack of plates - you add to the top and remove from the top.
    """
    
    def __init__(self):
        """
        Initialize an empty stack.
        """
        self.array = ArrayList()
        pass
    
    def push(self, item):
        """
        Add an item to the top of the stack.
        
        Args:
            item: The item to add to the stack
        """
        self.array.append(item)
        pass
    
    def pop(self):
        """
        Remove and return the top item from the stack.
        
        Returns:
            The item that was on top of the stack, or None if empty
        """
        if self.array.is_empty():
            return None
        value = self.array.pop()
        return value
    
    def peek(self):
        """
        Return the top item without removing it.
        
        Returns:
            The item on top of the stack, or None if empty
        """
        value = self.array.peek()

        return value
    
    def is_empty(self):
        """
        Check if the stack is empty.
        
        Returns:
            bool: True if stack is empty, False otherwise
        """
        is_empty = self.array.is_empty()
        return is_empty
    
    def size(self):
        """
        Get the number of items in the stack.
        
        Returns:
            int: The number of items currently in the stack
        """
        return self.array.size
    
    def clear(self):
        """Remove all items from the stack."""
        self.array.clear()
        pass
    
    def __str__(self):
        """String representation of the stack (for debugging)."""
        return f"{self.array[0:self.array.size]}"