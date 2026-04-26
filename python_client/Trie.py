# client/trie.py

class TrieNode:
    def __init__(self):
        """
        Each node represents a single character in a username.
        It holds references to children nodes and a flag for the end of a word.
        """
        self.children = {} # Dictionary to store child nodes {char: TrieNode}
        self.is_end_of_username = False # True if this node is the last char of a valid name

class PlayerTrie:
    def __init__(self):
        """
        Initialize the root of the Trie.
        """
        self.root = TrieNode()

    def insert(self, username):
        """
        Insert a new username into the Trie (Sign-up logic).
        Time Complexity: O(L) where L is the length of the username.
        """
        node = self.root
        for char in username:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_username = True

    def search(self, username):
        """
        Check if a username exists exactly in the Trie (Login logic).
        Returns: True if found, False otherwise.
        """
        node = self.root
        for char in username:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_username

    def starts_with(self, prefix):
        """
        Check if there is any username in the Trie that starts with the given prefix.
        Useful for real-time validation or simple existence checks.
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def get_all_with_prefix(self, prefix):
        """
        Retrieve all usernames that start with the given prefix (Autocomplete logic).
        Used for the 'Search Player' feature.
        """
        results = []
        node = self.root
        
        # 1. Navigate to the end of the prefix
        for char in prefix:
            if char not in node.children:
                return [] # No matches found
            node = node.children[char]
        
        # 2. Perform DFS from that node to find all complete usernames
        self._dfs(node, prefix, results)
        return results

    def _dfs(self, node, current_path, results):
        """
        Helper function for prefix search using Depth First Search.
        """
        if node.is_end_of_username:
            results.append(current_path)
        
        for char, next_node in node.children.items():
            self._dfs(next_node, current_path + char, results)