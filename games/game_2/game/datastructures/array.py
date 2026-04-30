<<<<<<< HEAD
"""
!!!This is an updated file from Lab 4!!!

arraylist.py - Dynamic Array Implementation

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
            self.data[index] = value
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
||||||| 82bc39c
=======
"""
arraylist.py - Dynamic Array Implementation

Students implement a dynamic array (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: Michael Janeczko
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
        Initializes an empty ArrayList with an initial capacity.
        """
        # TODO: Initialize instance variables
        self._array = [None] * initial_capacity
        self._capacity = initial_capacity
        self._size = 0
    
    # Returns the number of elements when you call len(my_array)
    def __len__(self):
        """
        Return the number of elements in ArrayList.
        """
        # TODO: Return the size
        return self._size
    
    # Enables bracket notation for accessing elements: my_array[3]
    def __getitem__(self, index):
        """
        Gets the element at a certain index.
        """
        # TODO: Return element at index
        if index < 0 or index >= self._size:
            return None
        return self._array[index]
    
    # Enables bracket notation for setting elements: my_array[3] = 42
    def __setitem__(self, index, value):
        """
        Sets the element at a certain index to a certain value.
        """
        # TODO: Set element at index
        if index < 0 or index >= self._size:
            return
        self._array[index] = value
    
    def append(self, value):
        """
        Appends an element to the end of ArrayList.
        """
        if self._size == self._capacity:
            self._resize()
        self._array[self._size] = value
        self._size += 1
    
    def insert(self, index, value):
        """
        Inserts an element at a certain index and shifts the rest of the elements to the right.
        """
        if index < 0 or index > self._size:
            return
        
        if self._size == self._capacity:
            self._resize()
        
        for i in range(self._size, index, -1):
            self._array[i] = self._array[i - 1]
        
        self._array[index] = value
        self._size += 1
    
    def remove(self, value):
        """
        Removes the first instance of a certain value.
        """
        for i in range(self._size):
            if self._array[i] == value:
                for j in range(i, self._size - 1):
                    self._array[j] = self._array[j + 1]
                self._size -= 1
                return
    
    def pop(self, index=-1):
        """
        Pops an element at a certain index.
        """
        if self._size == 0:
            return None
        
        if index < 0:
            index = self._size + index
        
        if index < 0 or index >= self._size:
            return None
        
        value = self._array[index]
        
        for i in range(index, self._size - 1):
            self._array[i] = self._array[i + 1]
        
        self._size -= 1
        return value
    
    def clear(self):
        """
        Removes all elements from ArrayList.
        """
        self._size = 0
    
    def index(self, value):
        """
        Returns the index of the first instance of a certain value.
        """
        for i in range(self._size):
            if self._array[i] == value:
                return i
        return -1

    def count(self, value):
        """
        Returns the number of instances of a certain value.
        """
        count = 0
        for i in range(self._size):
            if self._array[i] == value:
                count += 1
        return count

    def extend(self, iterable):
        """
        Adds all elements from the iterable to ArrayList.
        """
        for item in iterable:
            self.append(item)
    
    # Makes the "in" operator work: if 5 in my_array:
    def __contains__(self, value):
        """
        Confirms whether or not a certain value is in ArrayList.
        """
        for i in range(self._size):
            if self._array[i] == value:
                return True
        return False
    
    # Returns a user-friendly string representation when you call str(my_array) or print(my_array)
    def __str__(self):
        """
        Return a user-friendly string representation of ArrayList.
        """
        result = []
        for i in range(self._size):
            result.append(self._array[i])
        return str(result)
    
    # Returns a developer-friendly string representation (often the same as __str__ for simple classes), 
    # used in the interactive shell
    def __repr__(self):
        """
        Returns a developer-friendly string representation of ArrayList.
        """
        result = []
        for i in range(self._size):
            result.append(self._array[i])
        return "ArrayList(" + str(result) + ")"
    
    # Makes the list iterable so you can use it in for loops: for item in my_array:
    def __iter__(self):
        """
        Returns an iterator of the elements of ArrayList.
        """
        for i in range(self._size):
            yield self._array[i]
    
    def _resize(self):
        """
        Resizes the array when full capacity is reached.
        """
        self._capacity *= 2
        new_array = [None] * self._capacity
        
        new_array[:self._size] = self._array[:self._size]
        
        self._array = new_array
>>>>>>> origin/main
