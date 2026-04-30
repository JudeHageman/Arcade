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
