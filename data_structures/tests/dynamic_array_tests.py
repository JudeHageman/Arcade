# code/datastructures/tests/dynamic_array_tests.py

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dynamic_array import ArrayList

def test_array_creation():
    """Test creating an ArrayList"""
    print("Testing ArrayList creation...")
    
    arr = ArrayList()
    assert len(arr) == 0, "New ArrayList should have size 0"
    assert arr.capacity == 10, "Default capacity should be 10"
    
    arr2 = ArrayList(initial_capacity=5)
    assert arr2.capacity == 5, "Custom capacity should be 5"
    
    print("✓ ArrayList creation works!")

def test_append_and_len():
    print("Testing append and len...")
    arr = ArrayList(2)
    arr.append(1)
    arr.append(2)
    assert len(arr) == 2, "Size should be 2"
    assert arr[0] == 1 and arr[1] == 2, "Values not appended correctly"
    
    # Trigger resize
    arr.append(3)
    assert arr.capacity >= 3, "Capacity should have increased"
    assert arr[2] == 3, "Appended value not correct after resize"
    
    print("✓ Append and len works!")

def test_insert():
    print("Testing insert...")
    arr = ArrayList(3)
    arr.append(1)
    arr.append(3)
    arr.insert(1, 2)  # insert in middle
    assert arr[0] == 1 and arr[1] == 2 and arr[2] == 3, "Insert in middle failed"

    arr.insert(0, 0)  # insert at start
    assert arr[0] == 0, "Insert at start failed"

    arr.insert(len(arr), 4)  # insert at end
    assert arr[len(arr)-1] == 4, "Insert at end failed"

    print("✓ Insert works!")

def test_pop():
    print("Testing pop...")
    arr = ArrayList()
    arr.append(1)
    arr.append(2)
    arr.append(3)
    
    val = arr.pop()
    assert val == 3 and len(arr) == 2, "Pop without index failed"

    val = arr.pop(0)
    assert val == 1 and len(arr) == 1 and arr[0] == 2, "Pop at index failed"

    val = arr.pop(-1)
    assert len(arr) == 0, "Pop last element failed"

    print("✓ Pop works!")

def test_remove_and_count():
    print("Testing remove and count...")
    arr = ArrayList()
    arr.append(1)
    arr.append(2)
    arr.append(1)
    
    assert arr.count(1) == 2, "Count failed"
    arr.remove(1)
    assert arr.count(1) == 1, "Remove failed"
    
    try:
        arr.remove(99)
    except ValueError:
        pass
    else:
        assert False, "Remove non-existent value should raise ValueError"
    
    print("✓ Remove and count works!")

def test_contains_and_iter():
    print("Testing __contains__ and iteration...")
    arr = ArrayList()
    arr.append(1)
    arr.append(2)
    
    assert 1 in arr, "__contains__ failed"
    assert 3 not in arr, "__contains__ failed for missing value"

    s = 0
    for x in arr:
        s += x
    assert s == 3, "Iteration failed"

    print("✓ __contains__ and iteration work!")

def test_extend():
    print("Testing extend...")
    arr = ArrayList()
    arr.extend([1, 2, 3])
    assert len(arr) == 3 and arr[0] == 1 and arr[2] == 3, "Extend failed"

    arr.extend([])
    assert len(arr) == 3, "Extend with empty iterable failed"

    print("✓ Extend works!")

def test_edge_cases():
    """Edge cases"""
    print("Testing edge cases...")
    arr = ArrayList(1)
    
    # Pop from empty list should raise
    try:
        arr.pop()
    except IndexError:
        pass
    else:
        assert False, "Pop from empty array should raise IndexError"

    # Insert at negative index (invalid)
    try:
        arr.insert(-2, 10)
    except IndexError:
        pass
    else:
        assert False, "Insert at invalid negative index should raise IndexError"

    # Remove value not present
    arr.append(5)
    try:
        arr.remove(10)
    except ValueError:
        pass
    else:
        assert False, "Remove non-existent value should raise ValueError"

    # Append enough to trigger multiple resizes
    for i in range(20):
        arr.append(i)
    assert arr.capacity >= 21, "Multiple resizes failed"

    # Clear array
    arr.clear()
    assert len(arr) == 0, "Clear failed"

    print("✓ Edge cases passed!")

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running ArrayList Tests")
    print("="*50)
    
    test_array_creation()
    test_append_and_len()
    test_insert()
    test_pop()
    test_remove_and_count()
    test_contains_and_iter()
    test_extend()
    test_edge_cases()
    
    print("="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()
