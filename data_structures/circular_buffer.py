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