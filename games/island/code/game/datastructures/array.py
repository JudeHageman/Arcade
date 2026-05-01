"""
arraylist.py - Dynamic Array Implementation

Students implement a dynamic array (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: [Minju Seo]
Date: [2026-02-08]
Lab: Lab 3 - ArrayList and Inventory System
"""

class ArrayList:
    """
    Implement the methods discussed here: 
    https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """
    
    def __init__(self, initial_capacity=10):
        """
        Initializes the dynamic array with a fixed capacity.
        
        Args:
            initial_capacity (int): The initial size of the internal storage.
        """
        self.capacity = initial_capacity  # 배열이 담을 수 있는 총 크기
        self.size = 0                     # 실제 들어있는 요소의 개수
        # 내부 저장소: 초기 용량만큼 None으로 채워진 리스트 생성
        self.data = [None] * self.capacity 
    
    def get_capacity(self):
        """
        Returns the current capacity of the list.
        """
        return self.capacity
    
    def __len__(self):
        """
        Returns the number of elements in the list.
        """
        return self.size
    
    def __getitem__(self, index):
        """
        Retrieves the element at the specified index.
        Supports negative indexing.
        """
        if index < 0:
            index += self.size
            
        if not (0 <= index < self.size):
            raise IndexError("ArrayList index out of range")
            
        return self.data[index]
    
    def __setitem__(self, index, value):
        """
        Sets the element at the specified index to a new value.
        """
        if index < 0:
            index += self.size
            
        if not (0 <= index < self.size):
            raise IndexError("ArrayList index out of range")
            
        self.data[index] = value
    
    def _resize(self, new_capacity):
        """
        Internal helper method to resize the underlying storage.
        Creates a larger array and copies existing elements over.
        """
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity

    def append(self, value):
        """
        Adds an item to the end of the list.
        """
        # 공간이 꽉 찼으면 2배로 늘림
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
            
        self.data[self.size] = value
        self.size += 1
    
    def insert(self, index, value):
        """
        Inserts an item at a given position.
        """
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
            
        if index < 0: index += self.size
        # 범위를 벗어나면 맨 뒤나 맨 앞에 붙임 (파이썬 리스트 동작 방식)
        if index > self.size: index = self.size
        if index < 0: index = 0

        # 뒤에서부터 index까지 한 칸씩 뒤로 밀기
        for i in range(self.size, index, -1):
            self.data[i] = self.data[i-1]
            
        self.data[index] = value
        self.size += 1
    
    def remove(self, value):
        """
        Removes the first item from the list whose value is equal to x.
        Raises ValueError if there is no such item.
        """
        target_index = -1
        for i in range(self.size):
            if self.data[i] == value:
                target_index = i
                break
        
        if target_index == -1:
            raise ValueError(f"{value} not in list")
            
        # 찾은 위치 뒤의 요소들을 한 칸씩 앞으로 당김
        for i in range(target_index, self.size - 1):
            self.data[i] = self.data[i+1]
            
        self.data[self.size - 1] = None # 마지막 남은 찌꺼기 제거
        self.size -= 1
    
    def pop(self, index=-1):
        """
        Removes the item at the given position in the list, and returns it.
        If no index is specified, removes and returns the last item.
        """
        if index < 0:
            index += self.size
            
        if not (0 <= index < self.size):
            raise IndexError("pop index out of range")
            
        item = self.data[index]
        
        # 뒤의 요소들을 앞으로 당김
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i+1]
            
        self.data[self.size - 1] = None
        self.size -= 1
        return item
    
    def clear(self):
        """
        Removes all items from the list.
        """
        self.data = [None] * self.capacity
        self.size = 0
    
    def index(self, value):
        """
        Returns zero-based index in the list of the first item whose value is equal to x.
        Raises a ValueError if there is no such item.
        """
        for i in range(self.size):
            if self.data[i] == value:
                return i
        raise ValueError(f"{value} is not in list")

    def count(self, value):
        """
        Returns the number of times x appears in the list.
        """
        count = 0
        for i in range(self.size):
            if self.data[i] == value:
                count += 1
        return count

    def extend(self, iterable):
        """
        Extend the list by appending all the items from the iterable.
        """
        for item in iterable:
            self.append(item)
    
    def __contains__(self, value):
        """
        Returns True if the list contains the value, False otherwise.
        """
        for i in range(self.size):
            if self.data[i] == value:
                return True
        return False
    
    def __str__(self):
        """
        Returns a string representation of the list in format [x, y, z].
        """
        result = "["
        for i in range(self.size):
            result += str(self.data[i])
            if i < self.size - 1:
                result += ", "
        result += "]"
        return result
    
    def __repr__(self):
        """
        Returns the official string representation of the object.
        """
        return self.__str__()
    
    def __iter__(self):
        """
        Returns an iterator for the list to allow looping.
        """
        for i in range(self.size):
            yield self.data[i]