import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "data_structures"))

# dynamic array for collecting search results
from dynamic_array import ArrayList

# prefix trie for username lookup
from prefix_trie import PrefixTrie

# custom hash table for username to team lookup
from hash_table import HashTable

# shared account and session data
import memory


# trie plus lookup table for player search
_trie = PrefixTrie()
_table = HashTable()

# load the initial player data from the accounts
for username, data in memory.accounts.items():
    _trie.insert(username)
    _table.put(username, data.get("team", "unknown"))

def search_players(prefix):
    """Return players whose usernames start with the given prefix."""

    if not _trie.starts_with(prefix):
        return []

    results = ArrayList()
    stack_nodes = ArrayList()
    stack_names = ArrayList()
    stack_nodes.append(_trie._find_node(prefix))
    stack_names.append(prefix)

    # Continue searching only while we have nodes AND we haven't hit our limit
    while len(stack_nodes) > 0 and len(results) < 20:
        node = stack_nodes.pop()
        current = stack_names.pop()
        
        if node is None:
            continue
            
        if node.is_end_of_word:
            try:
                team = _table.get(current)
            except KeyError:
                team = "unknown"
            
            entry = HashTable()
            entry.put("username", current)
            entry.put("team", team)
            results.append(entry)

        # Optimization: Check limit again before adding more children to the stack
        if len(results) >= 20:
            break

        for char, child in node.children.items():
            stack_nodes.append(child)
            stack_names.append(current + char)

    output = []
    for entry in results:
        output.append({"username": entry.get("username"), "team": entry.get("team")})
    return output

def get_player(username):
    """Return a player's profile data if the username exists."""

    try:
        _table.get(username)
    except KeyError:
        return None

    import profile as _profile
    data = _profile.get_profile(username)
    if data is None:
        return {"username": username, "team": _table.get(username)}

    result = {"username": username}
    for key, value in data.items():
        result[key] = value
    return result

def refresh():
    """Load any new accounts into the trie and lookup table."""

    for username, data in memory.new_accounts().items():
        _trie.insert(username)
        _table.put(username, data.get("team", "unknown"))

