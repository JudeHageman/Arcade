from dynamic_array import ArrayList

class PriorityQueue:
    def __init__(self):
        self.heap = ArrayList()

    def is_empty(self):
        return len(self.heap) == 0

    def push(self, value):
        """Adds a value and moves it up to maintain heap property."""
        self.heap.append(value)
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        """Removes and returns the minimum value."""
        if self.is_empty():
            raise IndexError("pop from empty priority queue")
        
        # Root is the minimum
        root_value = self.heap[0]
        
        # Move the last element to the root
        last_val = self.heap.pop()
        
        if not self.is_empty():
            # We use the internal data to set the new root
            # Note: Your ArrayList __setitem__ handles bounds checking
            self.heap.data[0] = last_val
            self._bubble_down(0)
            
        return root_value

    def _bubble_up(self, index):
        parent = (index - 1) // 2
        # If the current node is smaller than its parent, swap them
        if index > 0 and self.heap[index] < self.heap[parent]:
            self.heap.data[index], self.heap.data[parent] = \
                self.heap.data[parent], self.heap.data[index]
            self._bubble_up(parent)

    def _bubble_down(self, index):
        left = 2 * index + 1
        right = 2 * index + 2
        smallest = index

        # Check if left child is smaller than current smallest
        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left
            
        # Check if right child is smaller than current smallest
        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right

        # If the smallest is not the current node, swap and keep bubbling down
        if smallest != index:
            self.heap.data[index], self.heap.data[smallest] = \
                self.heap.data[smallest], self.heap.data[index]
            self._bubble_down(smallest)

    def peek(self):
        if self.is_empty():
            return None
        return self.heap[0]