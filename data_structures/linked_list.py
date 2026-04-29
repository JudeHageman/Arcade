class DoublyNode:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None
        self.size = 0

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_last(self, value):
        new_node = DoublyNode(value)
        if not self.head:
            self.head = self.tail = new_node
            self.size = 1
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
            self.size += 1

    def add_first(self, value):
        """Adds an element to the beginning of the list. O(1)"""
        new_node = DoublyNode(value)
        if self.is_empty():
            self.head = self.tail = new_node
            self.size = 1
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1

    def remove_first(self):
        if not self.head: return None
        val = self.head.value
        self.head = self.head.next
        self.size -= 1
        if self.head: self.head.prev = None
        return val
    
    def remove_last(self):
        if not self.tail: return None
        val = self.tail.value
        self.tail = self.tail.prev
        self.size -= 1
        if self.tail: self.tail.next = None
        return val
    
    def is_empty(self):
        return self.size == 0
    
    def __str__(self):
        nodes = []
        curr = self.head
        while curr:
            nodes.append(str(curr.value))
            curr = curr.next
        return " <-> ".join(nodes)
    
