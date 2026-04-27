# filepath: data_structures/tests/circular_buffer_tests.py

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from circular_buffer import CircularBuffer

def test_buffer_creation():
    """Test creating a CircularBuffer"""
    print("Testing CircularBuffer creation...")
    
    cb = CircularBuffer(5)
    assert cb.capacity == 5, "Capacity should be 5"
    assert cb.size == 0, "Initial size should be 0"
    assert cb.head == 0, "Initial head should be 0"
    assert cb.tail == 0, "Initial tail should be 0"
    
    print("✓ CircularBuffer creation works!")

def test_enqueue_single():
    print("Testing single enqueue...")
    cb = CircularBuffer(3)
    cb.enqueue(1)
    assert cb.size == 1, "Size should be 1"
    assert cb.buffer.data[0] == 1, "First element should be 1"
    
    print("✓ Single enqueue works!")

def test_enqueue_multiple():
    print("Testing multiple enqueue...")
    cb = CircularBuffer(3)
    cb.enqueue(1)
    cb.enqueue(2)
    cb.enqueue(3)
    assert cb.size == 3, "Size should be 3"
    assert cb.buffer.data[0] == 1, "First element should be 1"
    assert cb.buffer.data[1] == 2, "Second element should be 2"
    assert cb.buffer.data[2] == 3, "Third element should be 3"
    
    print("✓ Multiple enqueue works!")

def test_enqueue_overwrite():
    """Test enqueue when buffer is full (overwrite oldest)"""
    print("Testing enqueue overwrite...")
    cb = CircularBuffer(3)
    cb.enqueue(1)
    cb.enqueue(2)
    cb.enqueue(3)
    cb.enqueue(4)  # Overwrites 1
    
    assert cb.size == 3, "Size should remain 3"
    assert cb.dequeue() == 2, "First dequeue should be 2 (1 was overwritten)"
    assert cb.dequeue() == 3, "Second dequeue should be 3"
    assert cb.dequeue() == 4, "Third dequeue should be 4"
    
    print("✓ Enqueue overwrite works!")

def test_dequeue():
    print("Testing dequeue...")
    cb = CircularBuffer(3)
    cb.enqueue(1)
    cb.enqueue(2)
    cb.enqueue(3)
    
    val = cb.dequeue()
    assert val == 1, "Dequeued value should be 1"
    assert cb.size == 2, "Size should be 2 after dequeue"
    
    print("✓ Dequeue works!")

def test_dequeue_empty():
    """Test dequeue from empty buffer"""
    print("Testing dequeue from empty buffer...")
    cb = CircularBuffer(3)
    
    try:
        cb.dequeue()
    except IndexError as e:
        assert "Empty Buffer" in str(e), "Error message should mention empty"
    else:
        assert False, "Should raise IndexError for empty buffer"
    
    print("✓ Dequeue empty works!")

def test_enqueue_dequeue_cycle():
    """Test cycling through buffer multiple times"""
    print("Testing enqueue/dequeue cycle...")
    cb = CircularBuffer(3)
    
    # Fill buffer
    cb.enqueue(1)
    cb.enqueue(2)
    cb.enqueue(3)
    
    # Dequeue one
    cb.dequeue()
    
    # Add two more
    cb.enqueue(4)
    cb.enqueue(5)
    
    # Should get 3, 4, 5 in order
    assert cb.dequeue() == 3, "Should be 3"
    assert cb.dequeue() == 4, "Should be 4"
    assert cb.dequeue() == 5, "Should be 5"
    
    print("✓ Enqueue/dequeue cycle works!")

def test_wrap_around():
    """Test buffer wrap-around behavior"""
    print("Testing wrap-around...")
    cb = CircularBuffer(3)
    
    cb.enqueue(1)
    cb.enqueue(2)
    cb.dequeue()  # Remove 1
    cb.dequeue()  # Remove 2
    
    # Now add more elements - should wrap around
    cb.enqueue(3)
    cb.enqueue(4)
    cb.enqueue(5)
    
    assert cb.dequeue() == 3, "Should be 3"
    assert cb.dequeue() == 4, "Should be 4"
    assert cb.dequeue() == 5, "Should be 5"
    
    print("✓ Wrap-around works!")

def test_mixed_operations():
    """Test mixed enqueue and dequeue operations"""
    print("Testing mixed operations...")
    cb = CircularBuffer(5)
    
    cb.enqueue(1)
    cb.enqueue(2)
    cb.enqueue(3) # cb = (1,2,3,_,_,)
    assert cb.dequeue() == 1, "Should be 1" # cb = (_,2,3,_,_,)
    
    cb.enqueue(4) # cb = (1,2,3,4,_,)
    cb.enqueue(5) # cb = (1,2,3,4,5,)
    cb.enqueue(6) # cb = (2,3,4,5,6,)
    cb.enqueue(7) # cb = (3,4,5,6,7,)
    
    # Should have 3, 4, 5, 6, 7
    assert cb.dequeue() == 3, "Should be 3"
    assert cb.dequeue() == 4, "Should be 4"
    assert cb.dequeue() == 5, "Should be 5"
    assert cb.dequeue() == 6, "Should be 6"
    assert cb.dequeue() == 7, "Should be 7"
    
    print("✓ Mixed operations work!")

def test_edge_cases():
    """Edge cases"""
    print("Testing edge cases...")
    
    # Capacity of 1
    cb1 = CircularBuffer(1)
    cb1.enqueue(1)
    cb1.enqueue(2)  # Overwrite
    assert cb1.dequeue() == 2, "Single capacity overwrite failed"
    
    # Multiple overwrites
    cb2 = CircularBuffer(2)
    for i in range(10):
        cb2.enqueue(i)
    
    # Should have 8 and 9
    assert cb2.dequeue() == 8, "Multiple overwrite failed"
    assert cb2.dequeue() == 9, "Multiple overwrite failed"
    
    # Empty after all dequeued
    cb3 = CircularBuffer(3)
    cb3.enqueue(1)
    cb3.dequeue()
    
    try:
        cb3.dequeue()
    except IndexError:
        pass
    else:
        assert False, "Should raise IndexError when empty"
    
    print("✓ Edge cases passed!")

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running CircularBuffer Tests")
    print("="*50)
    
    test_buffer_creation()
    test_enqueue_single()
    test_enqueue_multiple()
    test_enqueue_overwrite()
    test_dequeue()
    test_dequeue_empty()
    test_enqueue_dequeue_cycle()
    test_wrap_around()
    test_mixed_operations()
    test_edge_cases()
    
    print("="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()