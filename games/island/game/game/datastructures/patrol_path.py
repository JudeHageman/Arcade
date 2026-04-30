"""
patrol_path.py - Linked list implementation for NPC patrol paths

Implements different types of linked lists for NPC movement:
- Singly linked list (one-way patrol)
- Circular linked list (looping patrol)
- Doubly linked list (back-and-forth patrol)

Author: Minju seo
Date: 2026-04-02
Lab: Lab 5 - NPC Patrol Paths with Linked Lists
"""

from .waypoint import Waypoint


class PatrolPath:
    """
    A linked list of waypoints that defines how an NPC moves.
    """

    def __init__(self, patrol_type="circular"):
        """
        Initialize an empty patrol path.
        """
        self.head = None
        self.tail = None
        self.current = None
        self.patrol_type = patrol_type
        self.size = 0
        self.direction = 1  # 1 = forward, -1 = backward for back_and_forth

    def add_waypoint(self, x, y, wait_time=0):
        """
        Add a waypoint to the end of the patrol path.
        """
        # Create a new Waypoint node
        new_node = Waypoint(x, y, wait_time)

        if self.is_empty():
            # If the list is empty, set head, tail, and current to the new node
            self.head = new_node
            self.tail = new_node
            self.current = new_node
        else:
            # Link the new node after the current tail
            self.tail.next = new_node
            
            # For "back_and_forth" and "circular", set prev pointer on the new node
            # (Basically making it a doubly linked list structure where needed)
            if self.patrol_type in ["back_and_forth", "circular"]:
                new_node.prev = self.tail
            
            # Update tail to the new node
            self.tail = new_node

        # For "circular", close the loop
        if self.patrol_type == "circular":
            self.tail.next = self.head
            self.head.prev = self.tail

        self.size += 1

    def get_next_waypoint(self):
        """
        Get the next waypoint in the patrol sequence.
        """
        # If empty or current is None, return None
        if self.is_empty() or self.current is None:
            return None

        # Save current as result to return
        result = self.current

        # Logic for advancing to the next target
        if self.patrol_type == "one_way":
            # Advance to next (becomes None at the end of the list)
            self.current = self.current.next

        elif self.patrol_type == "circular":
            # Advance to next (wraps around because of the closed loop in add_waypoint)
            self.current = self.current.next

        elif self.patrol_type == "back_and_forth":
            if self.direction == 1:  # Moving Forward
                if self.current.next:
                    self.current = self.current.next
                else:
                    # Hit the end, reverse direction and move to previous
                    self.direction = -1
                    self.current = self.current.prev
            else:  # Moving Backward (direction == -1)
                if self.current.prev:
                    self.current = self.current.prev
                else:
                    # Hit the start, reverse direction and move to next
                    self.direction = 1
                    self.current = self.current.next

        return result

    def reset(self):
        """Reset patrol to the beginning."""
        self.current = self.head
        self.direction = 1

    def __len__(self):
        return self.size

    def __iter__(self):
        self._iter_current = self.head
        return self

    def __next__(self):
        if self._iter_current is None:
            raise StopIteration
        result = self._iter_current
        if self._iter_current == self.tail:
            self._iter_current = None
        else:
            self._iter_current = self._iter_current.next
        return result

    def is_empty(self):
        return self.head is None

    def get_path_info(self):
        return {
            "type": self.patrol_type,
            "length": len(self),
            "current": str(self.current) if self.current else "None",
            "direction": self.direction if self.patrol_type == "back_and_forth" else "N/A"
        }