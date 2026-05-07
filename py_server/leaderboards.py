import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "data_structures"))
sys.path.insert(0, str(Path(__file__).parent.parent / "algorithms"))

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

# player leaderboard trees and raw stats by game
_trees = HashTable()
_raw = HashTable()

# team leaderboard tree and raw team totals by game
_team_trees = HashTable()
_team_raw = HashTable()

MODES = ("best_score", "total_score", "play_time", "team_score")
PLAYER_MODES = ("best_score", "total_score", "play_time")


class LeaderboardEntry:
    """Store one player leaderboard row for BST ordering."""

    __slots__ = ("score", "username")

    def __init__(self, score, username):
        self.score = score
        self.username = username

    def __lt__(self, other):
        """Order higher scores first and break ties by username."""
        if self.score != other.score:
            return self.score > other.score
        return self.username < other.username

def _team_entry(score, team):
    """Build BST key for team leaderboard (higher score first)."""
    return (-score, team)

def _team_from_session(session):
    """Resolve team from session payload, then accounts fallback."""
    team = session.get("team", "")
    if team:
        return team
    username = session.get("username", "")
    return memory.accounts.get(username, {}).get("team", "")

# load initial session stats into caches
for session in memory.sessions:
    game = session.get("game")
    username = session.get("username")
    if not game or not username:
        continue

    # player cache
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

    # team cache
    team = _team_from_session(session)
    if team:
        try:
            game_team_raw = _team_raw.get(game)
        except KeyError:
            game_team_raw = HashTable()
            _team_raw.put(game, game_team_raw)

        try:
            total = game_team_raw.get(team)
        except KeyError:
            total = 0
        game_team_raw.put(team, total + session.get("team_score", 0))


# build player BSTs at startup
for i in range(_raw.capacity):
    for game, game_raw in _raw.table[i]:
        game_trees = HashTable()
        for key in PLAYER_MODES:
            game_trees.put(key, BST())
        _trees.put(game, game_trees)

        for j in range(game_raw.capacity):
            for username, stats in game_raw.table[j]:
                game_trees.get("best_score").insert(LeaderboardEntry(stats["best_score"], username))
                game_trees.get("total_score").insert(LeaderboardEntry(stats["total_score"], username))
                game_trees.get("play_time").insert(LeaderboardEntry(stats["play_time"], username))


# build team BSTs at startup
for i in range(_team_raw.capacity):
    for game, game_team_raw in _team_raw.table[i]:
        tree = BST()
        _team_trees.put(game, tree)
        for j in range(game_team_raw.capacity):
            for team, score in game_team_raw.table[j]:
                tree.insert(_team_entry(score, team))


def _iter_tree(tree):
    """In-order traversal yielding nodes in rank order (highest first)."""
    stack = ArrayList()
    node = tree.root
    while len(stack) or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        yield node
        node = node.right


def get_leaderboard(game_name, top_n=10, sort_by="best_score"):
    """Return leaderboard rows for one game and one mode."""
    if sort_by not in MODES:
        sort_by = "best_score"

    if sort_by == "team_score":
        try:
            tree = _team_trees.get(game_name)
        except KeyError:
            return []
        output = []
        for node in _iter_tree(tree):
            output.append({"team": node.value[1], "score": -node.value[0]})
            if len(output) >= top_n:
                break
        return output

    try:
        tree = _trees.get(game_name).get(sort_by)
    except KeyError:
        return []

    output = []
    for node in _iter_tree(tree):
        output.append({"username": node.value.username, "score": node.value.score})
        if len(output) >= top_n:
            break
    return output


def get_own_rank(game_name, username, sort_by="best_score"):
    """Return current user's rank for one game and one mode."""
    if sort_by not in MODES:
        sort_by = "best_score"

    if sort_by == "team_score":
        team_name = memory.accounts.get(username, {}).get("team", "")
        if not team_name:
            return None
        try:
            tree = _team_trees.get(game_name)
        except KeyError:
            return None

        count = 0
        for node in _iter_tree(tree):
            count += 1
            if node.value[1] == team_name:
                return count
        return None

    try:
        tree = _trees.get(game_name).get(sort_by)
    except KeyError:
        return None

    count = 0
    for node in _iter_tree(tree):
        count += 1
        if node.value.username == username:
            return count
    return None


def get_players_in_score_range(game_name, low, high, sort_by="best_score"):
    """Return players whose score falls between the given bounds."""
    if sort_by not in PLAYER_MODES:
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
    """Return list of games currently present in leaderboard caches."""
    games = ArrayList()
    for i in range(_trees.capacity):
        for name, _ in _trees.table[i]:
            games.append(name)
    output = []
    for name in games:
        output.append(name)
    return output


def refresh():
    """Process new sessions and update leaderboard caches."""
    for session in memory.new_sessions():
        game = session.get("game")
        username = session.get("username")
        if not game or not username:
            continue

        # player cache update
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
            for key in PLAYER_MODES:
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

        stats["total_score"] = total_score
        stats["play_time"] = total_play_time
        stats["games"] = stats["games"] + 1
        if score > best_score:
            best_score = score
            stats["best_score"] = best_score

        game_trees.get("best_score").insert(LeaderboardEntry(best_score, username))
        game_trees.get("total_score").insert(LeaderboardEntry(total_score, username))
        game_trees.get("play_time").insert(LeaderboardEntry(total_play_time, username))

        # team cache update
        team = _team_from_session(session)
        if not team:
            continue

        try:
            game_team_raw = _team_raw.get(game)
        except KeyError:
            game_team_raw = HashTable()
            _team_raw.put(game, game_team_raw)

        try:
            old_total = game_team_raw.get(team)
        except KeyError:
            old_total = 0

        new_total = old_total + session.get("team_score", 0)
        game_team_raw.put(team, new_total)

        try:
            team_tree = _team_trees.get(game)
        except KeyError:
            team_tree = BST()
            _team_trees.put(game, team_tree)

        if old_total > 0:
            team_tree.delete(_team_entry(old_total, team))
        team_tree.insert(_team_entry(new_total, team))
