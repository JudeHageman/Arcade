# filepath: data_structures/tests/priority_queue_tests.py

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data_structures')))

from priority_queue import PriorityQueue

def test_priority_queue_creation():
    """Test creating a PriorityQueue"""
    print("Testing PriorityQueue creation...")
    
    pq = PriorityQueue()
    assert len(pq.heap) == 0, "Heap should be empty"
    
    print("✓ PriorityQueue creation works!")

def test_push_single():
    print("Testing single push...")
    pq = PriorityQueue()
    pq.push(10)
    assert len(pq.heap) == 1, "Heap size should be 1"
    assert pq.heap[0] == 10, "First element should be 10"
    
    print("✓ Single push works!")

def test_push_multiple():
    print("Testing multiple pushes...")
    pq = PriorityQueue()
    pq.push(10)
    pq.push(5)
    pq.push(15)
    
    assert len(pq.heap) == 3, "Heap size should be 3"
    # Min-heap: smallest should be at root
    assert pq.heap[0] == 5, "Root should be smallest (5)"
    
    print("✓ Multiple pushes works!")

def test_push_order():
    """Test that push maintains min-heap property"""
    print("Testing push maintains heap property...")
    pq = PriorityQueue()
    
    # Insert in random order
    values = [50, 30, 70, 20, 40, 60, 80]
    for v in values:
        pq.push(v)
    
    # Root should always be minimum
    assert pq.heap[0] == 20, "Root should be minimum (20)"
    
    print("✓ Push maintains heap property!")

def test_pop_single():
    print("Testing single pop...")
    pq = PriorityQueue()
    pq.push(10)
    
    val = pq.pop()
    assert val == 10, "Popped value should be 10"
    assert len(pq.heap) == 0, "Heap should be empty after pop"
    
    print("✓ Single pop works!")

def test_pop_multiple():
    """Test that pop returns elements in priority order"""
    print("Testing multiple pops...")
    pq = PriorityQueue()
    
    pq.push(30)
    pq.push(10)
    pq.push(20)
    pq.push(50)
    pq.push(40)
    
    # Should come out in sorted order (min-heap)
    assert pq.pop() == 10, "First pop should be 10"
    assert pq.pop() == 20, "Second pop should be 20"
    assert pq.pop() == 30, "Third pop should be 30"
    assert pq.pop() == 40, "Fourth pop should be 40"
    assert pq.pop() == 50, "Fifth pop should be 50"
    
    print("✓ Multiple pops work!")

def test_pop_empty():
    """Test pop from empty queue"""
    print("Testing pop from empty queue...")
    pq = PriorityQueue()
    
    try:
        pq.pop()
    except IndexError as e:
        assert "Empty Queue" in str(e), "Error message should mention empty"
    else:
        assert False, "Should raise IndexError for empty queue"
    
    print("✓ Pop from empty works!")

def test_push_pop_sequence():
    """Test alternating push and pop"""
    print("Testing push/pop sequence...")
    pq = PriorityQueue()
    
    pq.push(5)
    pq.push(3)
    assert pq.pop() == 3, "First pop should be 3"
    
    pq.push(7)
    pq.push(1)
    assert pq.pop() == 1, "Next pop should be 1"
    assert pq.pop() == 5, "Next pop should be 5"
    
    print("✓ Push/pop sequence works!")

def test_heap_property_after_pop():
    """Test that heap property is maintained after pop"""
    print("Testing heap property after pop...")
    pq = PriorityQueue()
    
    # Insert values
    for v in [4, 2, 6, 1, 3, 5, 7]:
        pq.push(v)
    
    # Pop one and verify heap property
    pq.pop()
    
    # Verify root is still minimum
    assert pq.heap[0] == 2, "Root should be 2 after popping 1"
    
    # Pop more and verify
    pq.pop()
    assert pq.heap[0] == 3, "Root should be 3 after popping 2"
    
    print("✓ Heap property maintained after pop!")

def test_duplicates():
    """Test with duplicate values"""
    print("Testing duplicate values...")
    pq = PriorityQueue()
    
    pq.push(5)
    pq.push(3)
    pq.push(5)
    pq.push(1)
    
    assert pq.pop() == 1, "First pop should be 1"
    assert pq.pop() == 3, "Second pop should be 3"
    assert pq.pop() == 5, "Third pop should be 5"
    assert pq.pop() == 5, "Fourth pop should be 5"
    
    print("✓ Duplicate values work!")

def test_negative_numbers():
    """Test with negative numbers"""
    print("Testing negative numbers...")
    pq = PriorityQueue()
    
    pq.push(-5)
    pq.push(10)
    pq.push(-15)
    pq.push(0)
    
    assert pq.pop() == -15, "Minimum should be -15"
    assert pq.pop() == -5, "Next should be -5"
    assert pq.pop() == 0, "Next should be 0"
    assert pq.pop() == 10, "Maximum should be 10"
    
    print("✓ Negative numbers work!")

def test_strings():
    """Test with string values"""
    print("Testing string values...")
    pq = PriorityQueue()
    
    pq.push("banana")
    pq.push("apple")
    pq.push("cherry")
    
    # Strings are compared lexicographically
    assert pq.pop() == "apple", "First pop should be 'apple'"
    assert pq.pop() == "banana", "Second pop should be 'banana'"
    assert pq.pop() == "cherry", "Third pop should be 'cherry'"
    
    print("✓ String values work!")

def test_edge_cases():
    """Edge cases"""
    print("Testing edge cases...")
    
    # Single element
    pq1 = PriorityQueue()
    pq1.push(1)
    assert pq1.pop() == 1, "Single element failed"
    
    # Two elements
    pq2 = PriorityQueue()
    pq2.push(2)
    pq2.push(1)
    assert pq2.pop() == 1, "Two elements failed"
    assert pq2.pop() == 2, "Two elements failed"
    
    # Large number of elements
    pq3 = PriorityQueue()
    for i in range(100, 0, -1):
        pq3.push(i)
    
    # Should come out in order 1-100
    prev = 0
    for i in range(100):
        val = pq3.pop()
        assert val == i + 1, f"Expected {i+1}, got {val}"
    
    print("✓ Edge cases passed!")

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running PriorityQueue Tests")
    print("="*50)
    
    test_priority_queue_creation()
    test_push_single()
    test_push_multiple()
    test_push_order()
    test_pop_single()
    test_pop_multiple()
    test_pop_empty()
    test_push_pop_sequence()
    test_heap_property_after_pop()
    test_duplicates()
    test_negative_numbers()
    test_strings()
    test_edge_cases()
    
    print("="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()