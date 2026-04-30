# filepath: data_structures/tests/hash_table_tests.py

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data_structures')))

from hash_table import HashTable

def test_hash_table_creation():
    """Test creating a HashTable"""
    print("Testing HashTable creation...")
    
    ht = HashTable()
    assert ht.capacity == 10, "Default capacity should be 10"
    assert ht.size == 0, "Initial size should be 0"
    
    ht2 = HashTable(capacity=20)
    assert ht2.capacity == 20, "Custom capacity should be 20"
    
    print("✓ HashTable creation works!")

def test_put_single():
    print("Testing single put...")
    ht = HashTable()
    ht.put("apple", 5)
    assert ht.size == 1, "Size should be 1"
    assert ht.get("apple") == 5, "Value should be 5"
    
    print("✓ Single put works!")

def test_put_multiple():
    print("Testing multiple puts...")
    ht = HashTable()
    ht.put("apple", 5)
    ht.put("banana", 12)
    ht.put("cherry", 20)
    
    assert ht.size == 3, "Size should be 3"
    assert ht.get("apple") == 5, "Apple value should be 5"
    assert ht.get("banana") == 12, "Banana value should be 12"
    assert ht.get("cherry") == 20, "Cherry value should be 20"
    
    print("✓ Multiple puts works!")

def test_update_existing():
    """Test updating an existing key"""
    print("Testing update existing key...")
    ht = HashTable()
    ht.put("apple", 5)
    ht.put("apple", 10)  # Update
    
    assert ht.get("apple") == 10, "Value should be updated to 10"
    assert ht.size == 1, "Size should remain 1"
    
    print("✓ Update existing key works!")

def test_get_nonexistent():
    """Test getting a non-existent key"""
    print("Testing get non-existent key...")
    ht = HashTable()
    ht.put("apple", 5)
    
    try:
        ht.get("banana")
    except KeyError:
        pass
    else:
        assert False, "Should raise KeyError for non-existent key"
    
    print("✓ Get non-existent works!")

def test_collision_handling():
    """Test collision handling via chaining"""
    print("Testing collision handling...")
    ht = HashTable(capacity=2)  # Small capacity to force collisions
    
    # These might collide depending on hash function
    ht.put("a", 1)
    ht.put("b", 2)
    ht.put("c", 3)
    ht.put("d", 4)
    
    assert ht.get("a") == 1, "Value for a should be 1"
    assert ht.get("b") == 2, "Value for b should be 2"
    assert ht.get("c") == 3, "Value for c should be 3"
    assert ht.get("d") == 4, "Value for d should be 4"
    
    print("✓ Collision handling works!")

def test_various_key_types():
    """Test using different key types"""
    print("Testing various key types...")
    ht = HashTable()
    
    # String keys
    ht.put("name", "Alice")
    assert ht.get("name") == "Alice", "String key failed"
    
    # Integer keys
    ht.put(42, "answer")
    assert ht.get(42) == "answer", "Integer key failed"
    
    # Tuple keys
    ht.put((1, 2), "tuple key")
    assert ht.get((1, 2)) == "tuple key", "Tuple key failed"
    
    print("✓ Various key types work!")

def test_large_hash_table():
    """Test with many entries"""
    print("Testing large hash table...")
    ht = HashTable(capacity=50)
    
    for i in range(100):
        ht.put(f"key{i}", i)
    
    assert ht.size == 100, "Size should be 100"
    
    for i in range(100):
        assert ht.get(f"key{i}") == i, f"Value for key{i} should be {i}"
    
    print("✓ Large hash table works!")

def test_hash_function():
    """Test that hash function distributes keys"""
    print("Testing hash function distribution...")
    ht = HashTable(capacity=10)
    
    # Insert multiple keys
    ht.put("one", 1)
    ht.put("two", 2)
    ht.put("three", 3)
    ht.put("four", 4)
    ht.put("five", 5)
    
    # Verify all values accessible
    assert ht.get("one") == 1
    assert ht.get("two") == 2
    assert ht.get("three") == 3
    assert ht.get("four") == 4
    assert ht.get("five") == 5
    
    print("✓ Hash function works!")

def test_edge_cases():
    """Edge cases"""
    print("Testing edge cases...")
    
    # Empty string as key
    ht = HashTable()
    ht.put("", 0)
    assert ht.get("") == 0, "Empty string key failed"
    
    # Update same key multiple times
    ht.put("test", 1)
    ht.put("test", 2)
    ht.put("test", 3)
    assert ht.get("test") == 3, "Multiple updates failed"
    assert ht.size == 2, "Size should account for unique keys only"
    
    # Many unique keys
    ht2 = HashTable(capacity=5)
    for i in range(50):
        ht2.put(f"key{i}", i)
    assert ht2.size == 50, "Size should be 50"
    
    print("✓ Edge cases passed!")

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running HashTable Tests")
    print("="*50)
    
    test_hash_table_creation()
    test_put_single()
    test_put_multiple()
    test_update_existing()
    test_get_nonexistent()
    test_collision_handling()
    test_various_key_types()
    test_large_hash_table()
    test_hash_function()
    test_edge_cases()
    
    print("="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()