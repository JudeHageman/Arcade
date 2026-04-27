# filepath: data_structures/tests/linked_list_tests.py

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linked_list import LinkedList, DoublyNode

def test_linked_list_creation():
    """Test creating a LinkedList"""
    print("Testing LinkedList creation...")
    
    ll = LinkedList()
    assert ll.head is None, "Head should be None"
    assert ll.tail is None, "Tail should be None"
    
    print("✓ LinkedList creation works!")

def test_add_last_single():
    print("Testing single add_last...")
    ll = LinkedList()
    ll.add_last(10)
    
    assert ll.head is not None, "Head should not be None"
    assert ll.head.value == 10, "Head value should be 10"
    assert ll.tail == ll.head, "Tail should equal head for single element"
    
    print("✓ Single add_last works!")

def test_add_last_multiple():
    print("Testing multiple add_last...")
    ll = LinkedList()
    ll.add_last(10)
    ll.add_last(20)
    ll.add_last(30)
    
    assert ll.head.value == 10, "First value should be 10"
    assert ll.tail.value == 30, "Last value should be 30"
    assert ll.head.next.value == 20, "Second value should be 20"
    
    print("✓ Multiple add_last works!")

def test_remove_first_single():
    print("Testing single remove_first...")
    ll = LinkedList()
    ll.add_last(10)
    
    val = ll.remove_first()
    assert val == 10, "Removed value should be 10"
    assert ll.head is None, "Head should be None after removal"
    assert ll.tail is None, "Tail should be None after removal"
    
    print("✓ Single remove_first works!")

def test_remove_first_multiple():
    print("Testing multiple remove_first...")
    ll = LinkedList()
    ll.add_last(10)
    ll.add_last(20)
    ll.add_last(30)
    
    val = ll.remove_first()
    assert val == 10, "First removed should be 10"
    assert ll.head.value == 20, "Head should now be 20"
    
    val = ll.remove_first()
    assert val == 20, "Second removed should be 20"
    
    val = ll.remove_first()
    assert val == 30, "Third removed should be 30"
    assert ll.head is None, "Head should be None"
    
    print("✓ Multiple remove_first works!")

def test_remove_first_empty():
    """Test remove_first from empty list"""
    print("Testing remove_first from empty list...")
    ll = LinkedList()
    
    val = ll.remove_first()
    assert val is None, "Should return None from empty list"
    
    print("✓ Remove from empty works!")

def test_doubly_linked():
    """Test that nodes are properly linked both ways"""
    print("Testing doubly linked structure...")
    ll = LinkedList()
    ll.add_last(10)
    ll.add_last(20)
    ll.add_last(30)
    
    # Check forward links
    assert ll.head.next.value == 20, "Forward link to second node failed"
    assert ll.tail.prev.value == 20, "Backward link to second node failed"
    assert ll.head.prev is None, "Head prev should be None"
    assert ll.tail.next is None, "Tail next should be None"
    
    print("✓ Doubly linked structure works!")

def test_add_and_remove_sequence():
    """Test alternating add and remove operations"""
    print("Testing add and remove sequence...")
    ll = LinkedList()
    
    ll.add_last(1)
    ll.add_last(2)
    assert ll.remove_first() == 1
    
    ll.add_last(3)
    assert ll.remove_first() == 2
    assert ll.remove_first() == 3
    
    assert ll.head is None, "List should be empty"
    
    print("✓ Add and remove sequence works!")

def test_large_list():
    """Test with many elements"""
    print("Testing large list...")
    ll = LinkedList()
    
    for i in range(100):
        ll.add_last(i)
    
    # Remove half
    for i in range(50):
        assert ll.remove_first() == i, f"Remove failed for {i}"
    
    # Check remaining
    assert ll.head.value == 50, "Head should be 50"
    assert ll.tail.value == 99, "Tail should be 99"
    
    print("✓ Large list works!")

def test_edge_cases():
    """Edge cases"""
    print("Testing edge cases...")
    
    # Add after removing all
    ll = LinkedList()
    ll.add_last(1)
    ll.remove_first()
    ll.add_last(2)
    assert ll.head.value == 2, "Add after empty failed"
    assert ll.tail.value == 2, "Tail should be updated"
    
    # Add duplicate values
    ll2 = LinkedList()
    ll2.add_last(5)
    ll2.add_last(5)
    ll2.add_last(5)
    assert ll2.remove_first() == 5, "Duplicate value failed"
    assert ll2.remove_first() == 5, "Duplicate value failed"
    assert ll2.remove_first() == 5, "Duplicate value failed"
    
    # Remove from single element multiple times
    ll3 = LinkedList()
    ll3.add_last(1)
    ll3.remove_first()
    result = ll3.remove_first()
    assert result is None, "Should return None for empty list"
    
    print("✓ Edge cases passed!")

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running LinkedList Tests")
    print("="*50)
    
    test_linked_list_creation()
    test_add_last_single()
    test_add_last_multiple()
    test_remove_first_single()
    test_remove_first_multiple()
    test_remove_first_empty()
    test_doubly_linked()
    test_add_and_remove_sequence()
    test_large_list()
    test_edge_cases()
    
    print("="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()