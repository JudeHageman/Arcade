# filepath: data_structures/tests/prefix_trie_tests.py

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prefix_trie import Trie, TrieNode

def test_trie_creation():
    """Test creating a Trie"""
    print("Testing Trie creation...")
    
    trie = Trie()
    assert trie.root is not None, "Root should not be None"
    assert len(trie.root.children) == 0, "Root should have no children"
    assert trie.root.is_end_of_word == False, "Root should not be end of word"
    
    print("✓ Trie creation works!")

def test_insert_single():
    print("Testing single insert...")
    trie = Trie()
    trie.insert("apple")
    
    # Check that path exists
    assert 'a' in trie.root.children, "First letter 'a' should exist"
    assert trie.root.children['a'].is_end_of_word == False, "'a' should not be end of word"
    
    print("✓ Single insert works!")

def test_insert_multiple():
    print("Testing multiple inserts...")
    trie = Trie()
    trie.insert("apple")
    trie.insert("banana")
    trie.insert("cherry")
    
    assert 'a' in trie.root.children, "'a' path should exist"
    assert 'b' in trie.root.children, "'b' path should exist"
    assert 'c' in trie.root.children, "'c' path should exist"
    
    print("✓ Multiple inserts works!")

def test_search_existing():
    print("Testing search for existing word...")
    trie = Trie()
    trie.insert("apple")
    trie.insert("app")
    trie.insert("application")
    
    assert trie.search("apple") == True, "Search for 'apple' should be True"
    assert trie.search("app") == True, "Search for 'app' should be True"
    assert trie.search("application") == True, "Search for 'application' should be True"
    
    print("✓ Search for existing word works!")

def test_search_nonexistent():
    print("Testing search for non-existent word...")
    trie = Trie()
    trie.insert("apple")
    
    assert trie.search("banana") == False, "Search for non-existent should be False"
    assert trie.search("appl") == False, "Search for partial should be False"
    assert trie.search("applepie") == False, "Search for longer should be False"
    
    print("✓ Search for non-existent works!")

def test_starts_with_prefix():
    print("Testing starts_with...")
    trie = Trie()
    trie.insert("apple")
    trie.insert("app")
    trie.insert("application")
    trie.insert("banana")
    
    assert trie.starts_with("app") == True, "Prefix 'app' should exist"
    assert trie.starts_with("appl") == True, "Prefix 'appl' should exist"
    assert trie.starts_with("ban") == True, "Prefix 'ban' should exist"
    assert trie.starts_with("cher") == True, "Prefix 'cher' should exist"
    assert trie.starts_with("xyz") == False, "Non-existent prefix should be False"
    
    print("✓ starts_with works!")

def test_prefix_vs_word():
    """Test that prefix and full word are distinguished"""
    print("Testing prefix vs word distinction...")
    trie = Trie()
    trie.insert("app")
    trie.insert("apple")
    
    # "app" is a complete word
    assert trie.search("app") == True, "'app' should be found"
    assert trie.search("appl") == False, "'appl' should not be found"
    assert trie.search("apple") == True, "'apple' should be found"
    
    # Check that "app" is marked as end of word but "appl" is not
    node = trie.root.children['a'].children['p'].children['p']
    assert node.is_end_of_word == True, "'app' should be end of word"
    
    print("✓ Prefix vs word distinction works!")

def test_empty_string():
    """Test with empty string"""
    print("Testing empty string...")
    trie = Trie()
    trie.insert("")
    
    assert trie.search("") == True, "Empty string should be found"
    assert trie.starts_with("") == True, "Empty prefix should return True"
    
    print("✓ Empty string works!")

def test_long_words():
    """Test with long words"""
    print("Testing long words...")
    trie = Trie()
    
    long_word = "supercalifragilisticexpialidocious"
    trie.insert(long_word)
    
    assert trie.search(long_word) == True, "Long word should be found"
    assert trie.search(long_word + "extra") == False, "Longer word should not be found"
    assert trie.starts_with("super") == True, "Prefix of long word should exist"
    
    print("✓ Long words work!")

def test_common_prefixes():
    """Test words with common prefixes"""
    print("Testing common prefixes...")
    trie = Trie()
    trie.insert("test")
    trie.insert("testing")
    trie.insert("tested")
    trie.insert("tester")
    trie.insert("text")
    trie.insert("texture")
    
    # All "test*" words should exist
    assert trie.search("test") == True
    assert trie.search("testing") == True
    assert trie.search("tested") == True
    assert trie.search("tester") == True
    
    # "text*" words should exist
    assert trie.search("text") == True
    assert trie.search("texture") == True
    
    # Prefixes
    assert trie.starts_with("test") == True
    assert trie.starts_with("text") == True
    assert trie.starts_with("tes") == True
    
    print("✓ Common prefixes work!")

def test_edge_cases():
    """Edge cases"""
    print("Testing edge cases...")
    
    # Single character
    trie = Trie()
    trie.insert("a")
    assert trie.search("a") == True, "Single char search failed"
    assert trie.starts_with("a") == True, "Single char prefix failed"
    
    # Insert same word twice
    trie2 = Trie()
    trie2.insert("hello")
    trie2.insert("hello")  # Should not cause issues
    assert trie2.search("hello") == True, "Duplicate insert failed"
    
    # Search for prefix that is also a word
    trie3 = Trie()
    trie3.insert("in")
    trie3.insert("inner")
    trie3.insert("input")
    assert trie3.starts_with("in") == True, "Prefix 'in' should work"
    assert trie3.search("in") == True, "Word 'in' should work"
    
    print("✓ Edge cases passed!")

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running PrefixTrie Tests")
    print("="*50)
    
    test_trie_creation()
    test_insert_single()
    test_insert_multiple()
    test_search_existing()
    test_search_nonexistent()
    test_starts_with_prefix()
    test_prefix_vs_word()
    test_empty_string()
    test_long_words()
    test_common_prefixes()
    test_edge_cases()
    
    print("="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()