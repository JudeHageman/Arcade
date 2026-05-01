"""
Binary Search Tree (BST) implementation in Python.
Author: Jude Hageman
Date: 4/22/2026

This file contains the implementation of a binary search tree (BST) data structure.
"""

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1 

class BST:
    def __init__(self):
        self.root = None

    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def _right_rotate(self, y):
        """
        Rotates a 'Left-Heavy' subtree to the right.
        """
        x = y.left
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))

        return x  # Return the new root of this subtree

    def _left_rotate(self, x):
        """
        Rotates a 'Right-Heavy' subtree to the left.
        """
        y = x.right
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    def insert(self, value):
        # --- Phase 1: Standard iterative BST insert, tracking the path ---
        new_node = Node(value)
        
        if not self.root:
            self.root = new_node
            return

        path = []  # Stack of nodes visited, bottom-up rebalancing later
        node = self.root

        while node:
            path.append(node)
            if value < node.value:
                if node.left is None:
                    node.left = new_node
                    break
                node = node.left
            else:
                if node.right is None:
                    node.right = new_node
                    break
                node = node.right

        # --- Phase 2: Walk back up the path, updating heights and rebalancing ---
        for node in reversed(path):
            node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
            balance = self.get_balance(node)

            # Determine parent so we can rewire after a rotation
            parent = path[path.index(node) - 1] if path.index(node) > 0 else None

            new_subtree_root = None

            # Left Left
            if balance > 1 and self.get_balance(node.left) >= 0:
                new_subtree_root = self._right_rotate(node)
            # Left Right
            elif balance > 1 and self.get_balance(node.left) < 0:
                node.left = self._left_rotate(node.left)
                new_subtree_root = self._right_rotate(node)
            # Right Right
            elif balance < -1 and self.get_balance(node.right) <= 0:
                new_subtree_root = self._left_rotate(node)
            # Right Left
            elif balance < -1 and self.get_balance(node.right) > 0:
                node.right = self._right_rotate(node.right)
                new_subtree_root = self._left_rotate(node)

            # If a rotation happened, rewire the parent's pointer
            if new_subtree_root:
                if parent is None:
                    self.root = new_subtree_root
                elif parent.left is node:
                    parent.left = new_subtree_root
                else:
                    parent.right = new_subtree_root
    
    def delete(self, value):
        """Public method to delete a value."""
        self.root = self._delete_recursive(self.root, value)

    def _get_min_value_node(self, node):
        """Helper to find the node with the smallest value (leftmost)."""
        if node is None or node.left is None:
            return node
        return self._get_min_value_node(node.left)

    def _delete_recursive(self, root, value):
        # 1. Standard BST Delete logic
        if not root:
            return root

        if value < root.value:
            root.left = self._delete_recursive(root.left, value)
        elif value > root.value:
            root.right = self._delete_recursive(root.right, value)
        else:
            # Node with only one child or no child
            if root.left is None:
                temp = root.right
                root = None
                return temp
            elif root.right is None:
                temp = root.left
                root = None
                return temp

            # Node with two children: Get the inorder successor
            # (smallest in the right subtree)
            temp = self._get_min_value_node(root.right)
            root.value = temp.value
            root.right = self._delete_recursive(root.right, temp.value)

        if root is None:
            return root

        # 2. Update height of the current node
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        # 3. Get the balance factor
        balance = self.get_balance(root)

        # 4. Rebalance the tree (the 4 cases)
        
        # Case 1: Left Left
        if balance > 1 and self.get_balance(root.left) >= 0:
            return self._right_rotate(root)

        # Case 2: Left Right
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self._left_rotate(root.left)
            return self._right_rotate(root)

        # Case 3: Right Right
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self._left_rotate(root)

        # Case 4: Right Left
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self._right_rotate(root.right)
            return self._left_rotate(root)

        return root
    
    def contains(self, value):
        """Returns True if the value exists in the tree, False otherwise."""
        node = self.root
        while node:
            if value == node.value:
                return True
            node = node.left if value < node.value else node.right
        return False

    def _search_recursive(self, node, value):
        if not node:
            return False
        
        if value == node.value:
            return True
        
        if value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)