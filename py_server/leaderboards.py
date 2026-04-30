import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "data_structures"))
sys.path.insert(0, str(Path(__file__).parent.parent / "algorithms" / "sorting"))

# dynamic array used for ordered leaderboard output
from dynamic_array import ArrayList

# bst keeps each leaderboard sorted by score
from bst import BST

# mergesort used for score-range result ordering
from merge_sort import mergesort

# custom hash table for leaderboard state
from hash_table import HashTable

# shared account and session data
import memory

# leaderboard trees and raw stats by game
_trees = HashTable()
_raw = HashTable()

MODES = ("best_score", "total_score", "play_time")

class LeaderboardEntry:
    """Store one leaderboard row for BST ordering."""
    
    __slots__ = ("score", "username")

    def __init__(self, score, username):
        """Store the score and username used for leaderboard ordering."""
        self.score = score
        self.username = username

    def __lt__(self, other):
        """Order higher scores first and break ties by username."""
        if self.score != other.score:
            return self.score > other.score
        return self.username < other.username

# load the initial leaderboard state from the session
for session in memory.sessions:
    game = session.get("game")
    username = session.get("username")
    if not game or not username:
        continue

    try:
        game_raw = _raw.get(game)
    except KeyError:
        game_raw = HashTable()
        _raw.put(game, game_raw)

    try:
        stats = game_raw.get(username)
        is_new = False
    except KeyError:
        stats = HashTable()
        stats.put("best_score", 0)
        stats.put("total_score", 0)
        stats.put("play_time", 0)
        stats.put("games", 0)
        game_raw.put(username, stats)
        is_new = True

    try:
        game_trees = _trees.get(game)
    except KeyError:
        game_trees = HashTable()
        for key in MODES:
            game_trees.put(key, BST())
        _trees.put(game, game_trees)

    if not is_new:
        game_trees.get("best_score").delete(LeaderboardEntry(stats.get("best_score"), username))
        game_trees.get("total_score").delete(LeaderboardEntry(stats.get("total_score"), username))
        game_trees.get("play_time").delete(LeaderboardEntry(stats.get("play_time"), username))

    score = session.get("individual_score", 0)
    play_time = session.get("game_time", 0)
    best_score = stats.get("best_score")
    total_score = stats.get("total_score") + score
    total_play_time = stats.get("play_time") + play_time
    games_played = stats.get("games") + 1

    stats.put("total_score", total_score)
    stats.put("play_time", total_play_time)
    stats.put("games", games_played)
    if score > best_score:
        best_score = score
        stats.put("best_score", best_score)

    game_trees.get("best_score").insert(LeaderboardEntry(best_score, username))
    game_trees.get("total_score").insert(LeaderboardEntry(total_score, username))
    game_trees.get("play_time").insert(LeaderboardEntry(total_play_time, username))


def get_leaderboard(game_name, top_n=10, sort_by="best_score"):
    """Return the top players for one game and one leaderboard mode."""

    if sort_by not in MODES:
        sort_by = "best_score"
    try:
        tree = _trees.get(game_name).get(sort_by)
    except KeyError:
        return []
    results = ArrayList()
    stack = ArrayList()
    node = tree.root
    while len(stack) or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        entry = HashTable()
        entry.put("username", node.value.username)
        entry.put("score", node.value.score)
        results.append(entry)
        if len(results) >= top_n:
            break
        node = node.right
    output = []
    for entry in results:
        output.append({"username": entry.get("username"), "score": entry.get("score")})
    return output

def get_own_rank(game_name, username, sort_by="best_score"):
    """Return the rank of one player in a given leaderboard mode."""

    if sort_by not in MODES:
        sort_by = "best_score"
    try:
        tree = _trees.get(game_name).get(sort_by)
    except KeyError:
        return None
    count = 0
    stack = ArrayList()
    node = tree.root
    while len(stack) or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        count += 1
        if node.value.username == username:
            return count
        node = node.right
    return None

def get_players_in_score_range(game_name, low, high, sort_by="best_score"):
    """Return players whose score falls between the given bounds."""

    if sort_by not in MODES:
        sort_by = "best_score"
    try:
        tree = _trees.get(game_name).get(sort_by)
    except KeyError:
        return []
    results = ArrayList()
    stack = ArrayList()
    stack.append(tree.root)
    while len(stack):
        node = stack.pop()
        if node is None:
            continue
        score = node.value.score
        if low <= score <= high:
            entry = HashTable()
            entry.put("username", node.value.username)
            entry.put("score", score)
            results.append(entry)
        if score >= low:
            stack.append(node.right)
        if score <= high:
            stack.append(node.left)
    output = []
    for entry in results:
        output.append({"username": entry.get("username"), "score": entry.get("score")})
    return mergesort(output, key=lambda x: x["score"], reverse=True)

def get_all_games():
    """Return the list of games currently present in the leaderboard store."""

    games = ArrayList()
    for i in range(_trees.capacity):
        bucket = _trees.table[i]
        for name, _ in bucket:
            games.append(name)
    output = []
    for name in games:
        output.append(name)
    return output

def refresh():
    """Process any newly loaded sessions and update all leaderboard trees."""

    for session in memory.new_sessions():
        game = session.get("game")
        username = session.get("username")
        if not game or not username:
            continue

        try:
            game_raw = _raw.get(game)
        except KeyError:
            game_raw = HashTable()
            _raw.put(game, game_raw)

        try:
            stats = game_raw.get(username)
            is_new = False
        except KeyError:
            stats = HashTable()
            stats.put("best_score", 0)
            stats.put("total_score", 0)
            stats.put("play_time", 0)
            stats.put("games", 0)
            game_raw.put(username, stats)
            is_new = True

        try:
            game_trees = _trees.get(game)
        except KeyError:
            game_trees = HashTable()
            for key in MODES:
                game_trees.put(key, BST())
            _trees.put(game, game_trees)

        if not is_new:
            game_trees.get("best_score").delete(LeaderboardEntry(stats.get("best_score"), username))
            game_trees.get("total_score").delete(LeaderboardEntry(stats.get("total_score"), username))
            game_trees.get("play_time").delete(LeaderboardEntry(stats.get("play_time"), username))

        score = session.get("individual_score", 0)
        play_time = session.get("game_time", 0)
        best_score = stats.get("best_score")
        total_score = stats.get("total_score") + score
        total_play_time = stats.get("play_time") + play_time
        games_played = stats.get("games") + 1

        stats.put("total_score", total_score)
        stats.put("play_time", total_play_time)
        stats.put("games", games_played)
        if score > best_score:
            best_score = score
            stats.put("best_score", best_score)

        game_trees.get("best_score").insert(LeaderboardEntry(best_score, username))
        game_trees.get("total_score").insert(LeaderboardEntry(total_score, username))
        game_trees.get("play_time").insert(LeaderboardEntry(total_play_time, username))


