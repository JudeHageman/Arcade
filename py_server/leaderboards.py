import sys
from pathlib import Path

 

# dynamic array used for ordered leaderboard output
from dynamic_array import ArrayList

# bst keeps each leaderboard sorted by score
from bst import BST

# mergesort used for score-range result ordering
base_path = Path(__file__).parent.parent.parent.parent

# 1. 자료구조 경로 (Arcade/data_structures)
ds_path = str(base_path / "data_structures")
if ds_path not in sys.path:
    sys.path.insert(0, ds_path)

# 2. 알고리즘 경로 (Arcade/algorithms/sorting)
sorting_path = str(base_path / "algorithms" / "sorting")
if sorting_path not in sys.path:
    sys.path.insert(0, sorting_path)

# 임포트 시도
try:
    from dynamic_array import ArrayList
    from merge_sort import mergesort
    print("✅ Successfully imported ArrayList and MergeSort")
except ImportError as e:
    print(f"❌ Import failed: {e}")
 

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

# load initial session stats into _raw
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
    except KeyError:
        stats = {"best_score": 0, "total_score": 0, "play_time": 0, "games": 0}
        game_raw.put(username, stats)

    score = session.get("individual_score", 0)
    play_time = session.get("game_time", 0)

    stats["total_score"] += score
    stats["play_time"] += play_time
    stats["games"] += 1
    if score > stats["best_score"]:
        stats["best_score"] = score

# build each BST once at startup to avoid O(n log n) insert time during refresh
for i in range(_raw.capacity):
    for game, game_raw in _raw.table[i]:
        game_trees = HashTable()
        for key in MODES:
            game_trees.put(key, BST())
        _trees.put(game, game_trees)
        for j in range(game_raw.capacity):
            for username, stats in game_raw.table[j]:
                game_trees.get("best_score").insert(LeaderboardEntry(stats["best_score"], username))
                game_trees.get("total_score").insert(LeaderboardEntry(stats["total_score"], username))
                game_trees.get("play_time").insert(LeaderboardEntry(stats["play_time"], username))


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
            stats = {"best_score": 0, "total_score": 0, "play_time": 0, "games": 0}
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
            game_trees.get("best_score").delete(LeaderboardEntry(stats["best_score"], username))
            game_trees.get("total_score").delete(LeaderboardEntry(stats["total_score"], username))
            game_trees.get("play_time").delete(LeaderboardEntry(stats["play_time"], username))

        score = session.get("individual_score", 0)
        play_time = session.get("game_time", 0)
        best_score = stats["best_score"]
        total_score = stats["total_score"] + score
        total_play_time = stats["play_time"] + play_time
        games_played = stats["games"] + 1

        stats["total_score"] = total_score
        stats["play_time"] = total_play_time
        stats["games"] = games_played
        if score > best_score:
            best_score = score
            stats["best_score"] = best_score

        game_trees.get("best_score").insert(LeaderboardEntry(best_score, username))
        game_trees.get("total_score").insert(LeaderboardEntry(total_score, username))
        game_trees.get("play_time").insert(LeaderboardEntry(total_play_time, username))


