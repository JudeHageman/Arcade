import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "data_structures"))
sys.path.insert(0, str(Path(__file__).parent.parent / "algorithms" / "sorting"))

# custom hash table for game catalog data
from hash_table import HashTable

# heap sort used to sort games by popularity metrics
from heap_sort import heap_sort

# shared account and session data
import memory

# current game records and aggregate stats
_games = HashTable()
_stats = HashTable()

# load the initial game snapshot
for game_name, info in memory.games.items():
    _games.put(game_name, info)

# build the initial game stats from the session
for session in memory.sessions:
    game = session.get("game")
    if not game:
        continue
    try:
        stats = _stats.get(game)
    except KeyError:
        stats = {"total_sessions": 0, "_total_score": 0, "avg_score": 0.0, "last_played": ""}
        _stats.put(game, stats)

    stats["total_sessions"] += 1
    stats["_total_score"] += session.get("individual_score", 0)
    stats["avg_score"] = round(stats["_total_score"] / stats["total_sessions"], 2)

    timestamp = session.get("timestamp", "")
    if timestamp > stats["last_played"]:
        stats["last_played"] = timestamp

def get_game(game_name):
    """Return the stored game record for a given game name."""

    try:
        return _games.get(game_name)
    except KeyError:
        return None

def get_all_games():
    """Return every game with its aggregate session statistics."""

    result = []
    for i in range(_games.capacity):
        for name, info in _games.table[i]:
            try:
                stats = _stats.get(name)
                stats_dict = {"total_sessions": stats["total_sessions"], "avg_score": stats["avg_score"], "last_played": stats["last_played"]}
            except KeyError:
                stats_dict = {"total_sessions": 0, "avg_score": 0.0, "last_played": ""}
            result.append({"name": name, **info, **stats_dict})
    return result

def get_all_games_sorted(sort_by="most_played"):
    """Return all games ordered by the requested aggregate metric using heap sort."""

    key_map = {"most_played": "total_sessions", "highest_avg_score": "avg_score", "most_recently_active": "last_played"}
    key_name = key_map.get(sort_by, "total_sessions")
    return heap_sort(get_all_games(), key=lambda g: g.get(key_name, 0), reverse=True)

def refresh():
    """Append any newly loaded games and sessions into the in-memory snapshot."""

    for game_name, info in memory.new_games().items():
        _games.put(game_name, info)

    for session in memory.new_sessions():
        game = session.get("game")
        if not game:
            continue
        try:
            stats = _stats.get(game)
        except KeyError:
            stats = {"total_sessions": 0, "_total_score": 0, "avg_score": 0.0, "last_played": ""}
            _stats.put(game, stats)

        stats["total_sessions"] += 1
        stats["_total_score"] += session.get("individual_score", 0)
        stats["avg_score"] = round(stats["_total_score"] / stats["total_sessions"], 2)

        timestamp = session.get("timestamp", "")
        if timestamp > stats["last_played"]:
            stats["last_played"] = timestamp


