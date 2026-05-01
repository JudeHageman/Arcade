"""
waypoint.py - Waypoint node for linked list patrol paths

A waypoint represents a single point in an NPC's patrol path.
This serves as a node in our linked list data structure.

Author: Minju Seo
Date: 2026-04-02
Lab: Lab 5 - NPC Patrol Paths with Linked Lists
"""

import math

class Waypoint:
    """
    A single waypoint (node) in a patrol path.
    This serves as the building block for our linked list structures.
    """

    def __init__(self, x, y, wait_time=0):
        """
        Initialize a waypoint node with position and pointers.

        Args:
            x (float): X coordinate in the game world.
            y (float): Y coordinate in the game world.
            wait_time (float): Seconds the NPC pauses at this location.
        """
        # Store position and timing data
        self.x = x
        self.y = y
        self.wait_time = wait_time
        
        # Pointers for linked list traversal
        # Initially None until connected in PatrolPath
        self.next = None  # Pointer to the next waypoint
        self.prev = None  # Pointer to the previous waypoint (for doubly linked)

    def distance_to(self, other_x, other_y):
        """
        Calculate the Euclidean distance to another point.
        Used to check if the NPC has 'arrived' at this waypoint.

        Returns:
            float: The straight-line distance.
        """
        # Using the distance formula: sqrt((x2 - x1)^2 + (y2 - y1)^2)
        dx = other_x - self.x
        dy = other_y - self.y
        return math.sqrt(dx**2 + dy**2)

    def __str__(self):
        """String representation for debugging."""
        return f"Waypoint({self.x}, {self.y}, wait={self.wait_time})"

    def __repr__(self):
        return self.__str__()