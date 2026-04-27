from dynamic_array import ArrayList

class CircularBuffer:
    def __init__(self, capacity):
        self.buffer = ArrayList(capacity)
        for _ in range(capacity): self.buffer.append(None)
        self.capacity = capacity
        self.head = 0
        self.tail = 0
        self.size = 0

    def enqueue(self, value):
        self.buffer.data[self.tail] = value
        self.tail = (self.tail + 1) % self.capacity
        if self.size < self.capacity:
            self.size += 1
        else:
            self.head = (self.head + 1) % self.capacity # Overwrite

    def dequeue(self):
        if self.size == 0: raise IndexError("Empty Buffer")
        val = self.buffer.data[self.head]
        self.head = (self.head + 1) % self.capacity
        self.size -= 1
        return val
    
    def is_empty(self):
        return self.size == 0

    def is_full(self):
        return self.size == self.capacity
    
    def peek(self):
        """Returns the oldest item without removing it."""
        if self.is_empty():
            return None
        return self.buffer.data[self.head]

    def __str__(self):
        """Shows the buffer content in chronological order."""
        items = []
        for i in range(self.size):
            index = (self.head + i) % self.capacity
            items.append(self.buffer.data[index])
        return f"CircularBuffer: {items}"