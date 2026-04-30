class TrieNode:
    def __init__(self):
        # We use a dictionary for children to handle any character
        self.children = {}
        self.is_end_of_word = False

class PrefixTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """Inserts a word into the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        """Returns True if the word is in the trie."""
        node = self._find_node(word)
        return node is not None and node.is_end_of_word

    def starts_with(self, prefix):
        """Returns True if there is any word in the trie that starts with the prefix."""
        return self._find_node(prefix) is not None

    def _find_node(self, string):
        """Helper to navigate to the end of a string path."""
        node = self.root
        for char in string:
            if char not in node.children:
                return None
            node = node.children[char]
        return node