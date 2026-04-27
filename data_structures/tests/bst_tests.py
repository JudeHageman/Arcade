# filepath: data_structures/tests/bst_tests.py

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bst import BST

def test_bst_creation():
    """Test creating a BST"""
    print("Testing BST creation...")
    
    bst = BST()
    assert bst.root is None, "New BST should have None root"
    
    print("✓ BST creation works!")

def test_insert_single():
    print("Testing single insert...")
    bst = BST()
    bst.insert(10)
    assert bst.root is not None, "Root should not be None after insert"
    assert bst.root.value == 10, "Root value should be 10"
    
    print("✓ Single insert works!")

def test_insert_multiple():
    print("Testing multiple inserts...")
    bst = BST()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    
    assert bst.root.value == 10, "Root should be 10"
    assert bst.root.left.value == 5, "Left child should be 5"
    assert bst.root.right.value == 15, "Right child should be 15"
    
    print("✓ Multiple inserts works!")

def test_insert_unbalanced():
    """Test inserting values that would create an unbalanced tree (AVL rebalancing)"""
    print("Testing AVL rebalancing...")
    bst = BST()
    
    # Insert in increasing order - would cause right-heavy imbalance
    bst.insert(10)
    bst.insert(20)
    bst.insert(30)
    
    # After rebalancing, root should be 20 (the middle value)
    assert bst.root.value == 20, "Root should be rebalanced to 20"
    assert bst.root.left.value == 10, "Left child should be 10"
    assert bst.root.right.value == 30, "Right child should be 30"
    
    # Insert in decreasing order - would cause left-heavy imbalance
    bst2 = BST()
    bst2.insert(30)
    bst2.insert(20)
    bst2.insert(10)
    
    assert bst2.root.value == 20, "Root should be rebalanced to 20"
    assert bst2.root.left.value == 10, "Left child should be 10"
    assert bst2.root.right.value == 30, "Right child should be 30"
    
    print("✓ AVL rebalancing works!")

def test_insert_double_rotation():
    """Test double rotation cases (Left-Right and Right-Left)"""
    print("Testing double rotation...")
    
    # Left-Right case
    bst = BST()
    bst.insert(30)
    bst.insert(10)
    bst.insert(20)
    
    # After left-right rotation, root should be 20
    assert bst.root.value == 20, "Left-Right rotation failed"
    
    # Right-Left case
    bst2 = BST()
    bst2.insert(10)
    bst2.insert(30)
    bst2.insert(20)
    
    # After right-left rotation, root should be 20
    assert bst2.root.value == 20, "Right-Left rotation failed"
    
    print("✓ Double rotation works!")

def test_delete_no_children():
    """Test deleting a leaf node"""
    print("Testing delete with no children...")
    bst = BST()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    
    bst.delete(5)
    assert bst.root.left is None, "Left child should be None after delete"
    
    print("✓ Delete with no children works!")

def test_delete_one_child():
    """Test deleting a node with one child"""
    print("Testing delete with one child...")
    bst = BST()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.insert(3)  # Child of 5
    
    bst.delete(5)
    assert bst.root.left is not None, "Left child should exist after delete"
    assert bst.root.left.value == 3, "Left child should be 3"
    
    print("✓ Delete with one child works!")

def test_delete_two_children():
    """Test deleting a node with two children"""
    print("Testing delete with two children...")
    bst = BST()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.insert(3)
    bst.insert(7)
    
    # Delete node with two children (10)
    bst.delete(10)
    # The inorder successor (15) should replace the deleted node
    assert bst.root.value == 15, "Root should be replaced by inorder successor"
    
    print("✓ Delete with two children works!")

def test_delete_nonexistent():
    """Test deleting a non-existent value"""
    print("Testing delete of non-existent value...")
    bst = BST()
    bst.insert(10)
    bst.insert(20)
    
    # Should not raise an error, just do nothing
    bst.delete(99)
    assert bst.root.value == 10, "Tree should be unchanged"
    
    print("✓ Delete non-existent works!")

def test_height():
    """Test height calculation"""
    print("Testing height...")
    bst = BST()
    
    assert bst.get_height(bst.root) == 0, "Empty tree height should be 0"
    
    bst.insert(10)
    assert bst.get_height(bst.root) == 1, "Single node height should be 1"
    
    bst.insert(5)
    bst.insert(15)
    assert bst.get_height(bst.root) == 2, "Height should be 2"
    
    print("✓ Height calculation works!")

def test_balance():
    """Test balance factor calculation"""
    print("Testing balance factor...")
    bst = BST()
    
    bst.insert(10)
    assert bst.get_balance(bst.root) == 0, "Single node balance should be 0"
    
    bst.insert(5)
    bst.insert(15)
    # Balanced tree should have balance factor of 0
    balance = bst.get_balance(bst.root)
    assert abs(balance) <= 1, "Balanced tree should have |balance| <= 1"
    
    print("✓ Balance factor works!")

def test_edge_cases():
    """Edge cases"""
    print("Testing edge cases...")
    
    # Delete from empty tree
    bst = BST()
    bst.delete(10)  # Should not raise
    assert bst.root is None, "Empty tree should remain empty"
    
    # Insert duplicate values
    bst2 = BST()
    bst2.insert(10)
    bst2.insert(10)  # Should go to right
    assert bst2.root.value == 10, "First 10 should be root"
    assert bst2.root.right.value == 10, "Second 10 should be right child"
    
    # Large tree
    bst3 = BST()
    for i in range(100):
        bst3.insert(i)
    # Tree should still be balanced
    assert bst3.get_height(bst3.root) < 10, "Height should be limited with AVL"
    
    print("✓ Edge cases passed!")

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running BST Tests")
    print("="*50)
    
    test_bst_creation()
    test_insert_single()
    test_insert_multiple()
    test_insert_unbalanced()
    test_insert_double_rotation()
    test_delete_no_children()
    test_delete_one_child()
    test_delete_two_children()
    test_delete_nonexistent()
    test_height()
    test_balance()
    test_edge_cases()
    
    print("="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()