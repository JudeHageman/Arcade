"""
!!!This is an updated file from Lab 4!!!

dynamic_array.py - Dynamic Array Implementation

Students implement a dynamic array (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: Jude Hageman
Date: 2/11/2026
Lab: Lab 3 - ArrayList and Inventory System
"""

class ArrayList:
    """
    Implement the methods discussed here: 
    https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """
    
    def __init__(self, initial_capacity=10):
        """
        """
        # TODO: Initialize instance variables
        self.size = 0
        self.capacity = initial_capacity
        self.data = [None] * initial_capacity
        pass
    
    # Returns the number of elements when you call len(my_array)
    def __len__(self):
        """
        """
        # TODO: Return the size
        return self.size
    
    def resize(self):
        self.capacity*=2
        new_data = [None]*self.capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data

    def is_empty(self):
        """
        Checks to see if the array is empty.
        
        Returns:
            boolean
        """
        return self.size == 0
    
    # Enables bracket notation for accessing elements: my_array[3]
    def __getitem__(self, index):
        """
        """
        # TODO: Return element at index
        if index > self.size - 1:
            raise IndexError("Error! Index out of range")
        else:
            return self.data[index]
        pass

    
    # Enables bracket notation for setting elements: my_array[3] = 42
    def __setitem__(self, index, value):
        """
        """
        # TODO: Set element at index
        if index > self.size - 1:
            raise IndexError("Error! Index out of range")
        else:
            self.array[index] = value
        pass
    
    def append(self, value):
        """
        """
        if self.size == self.capacity:
            self.resize()
            self.data[self.size] = value
            self.size += 1
        else:
            self.data[self.size] = value
            self.size += 1
        pass
    
    def insert(self, index, value):
        """
        """
        if index > self.size:
            raise IndexError("Error! Index out of range")
        elif index == self.size:
            self.append(value)
        else:
            if self.size == self.capacity:
                self.resize()
            for i in range(self.size, index, -1):
                self.data[i] = self.data[i-1]
            self.size += 1
            self.data[index] = value
        pass
    
    def remove(self, value):
        """
        """
        index = -1
        for i in range(self.size):
            if self.data[i] == value:
                index = i
                break
        if index == -1:
            raise ValueError("Error! That value doesn't exist")
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]
        self.data[self.size - 1] = None
        self.size -= 1
        
    def pop(self, index=-1):
        """
        """
        if index < -self.size or index >= self.size:
            raise IndexError("Error! Index is out of range")
        if index < 0:
            index += self.size

        value = self.data[index]
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i+1]
        self.data[self.size-1] = None
        self.size -= 1
        return value
    
    def peek(self):
        return self.data[self.size-1]
    
    def clear(self):
        """
        """
        new_data = [None]*self.capacity
        self.size = 0
        self.data = new_data
        return self.data
    
    def index(self, value):
        """
        """
        index = -1
        for i in range(0, self.size):
            if self.data[i] == value:
                index = i
        if index == -1:
            raise ValueError("Error! No such value exists in array")
        return index

    def count(self, value):
        """
        """
        num = 0
        for i in range(0, self.size):
            if self.data[i] == value:
                num += 1
        return num

    def extend(self, iterable):
        """
        """
        for item in iterable:
            self.append(item)
        pass
    
    # Makes the "in" operator work: if 5 in my_array:
    def __contains__(self, value):
        """
        """
        for i in range(0, self.size):
            if self.data[i] == value:
                return True
        return False
    
    # Returns a user-friendly string representation when you call str(my_array) or print(my_array)
    def __str__(self):
        """
        """
        new_data = [None]*self.size
        for i in range(self.size):
            new_data[i] = self.data[i]
        return f"{new_data}"
    
    # Returns a developer-friendly string representation (often the same as __str__ for simple classes), 
    # used in the interactive shell
    def __repr__(self):
        """
        """
        new_data = [None]*self.size
        for i in range(self.size):
            new_data[i] = self.data[i]
        return f"ArrayList(size={self.size}, capacity={self.capacity}, data={new_data})"
    
    # Makes the list iterable so you can use it in for loops: for item in my_array:
    def __iter__(self):
        """
        """
        for i in range(self.size):
            yield self.data[i]
        pass