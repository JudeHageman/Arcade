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
        self.root = self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        # 1. Standard BST insertion
        if not node:
            return Node(value)
        
        if value < node.value:
            node.left = self._insert_recursive(node.left, value)
        else:
            node.right = self._insert_recursive(node.right, value)

        # 2. Update height of this ancestor node
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

        # 3. Get balance factor to check if it's unbalanced
        balance = self.get_balance(node)

        # 4. Handle 4 cases of imbalance
        
        # Case 1: Left Left (Single Right Rotation)
        if balance > 1 and value < node.left.value:
            return self._right_rotate(node)

        # Case 2: Right Right (Single Left Rotation)
        if balance < -1 and value > node.right.value:
            return self._left_rotate(node)

        # Case 3: Left Right (Double Rotation)
        if balance > 1 and value > node.left.value:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Case 4: Right Left (Double Rotation)
        if balance < -1 and value < node.right.value:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node
    
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
        return self._search_recursive(self.root, value)

    def _search_recursive(self, node, value):
        if not node:
            return False
        
        if value == node.value:
            return True
        
        if value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)