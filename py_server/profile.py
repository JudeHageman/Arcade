import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "data_structures"))

# dynamic array for recent score history
from dynamic_array import ArrayList

# custom hash table for profile data
from hash_table import HashTable

# shared account and session data
import memory

# player profile records
_profiles = HashTable()

def _new_profile(team):
    """Create a blank profile record for one player."""

    profile = HashTable()
    profile.put("team", team)
    profile.put("total_games", 0)
    profile.put("total_score", 0)
    profile.put("best_score", 0)
    profile.put("total_time", 0)
    profile.put("_per_game", HashTable())
    profile.put("win_rate_per_game", HashTable())
    profile.put("score_history", ArrayList())
    return profile

# load the initial profile state from the accounts and sessions
for username, data in memory.accounts.items():
    try:
        _profiles.get(username)
    except KeyError:
        _profiles.put(username, _new_profile(data.get("team", "unknown")))\
        
# apply each session to the relevant player's profile
for session in memory.sessions:
    username = session.get("username")
    if not username:
        continue
    try:
        profile = _profiles.get(username)
    except KeyError:
        profile = _new_profile("unknown")
        _profiles.put(username, profile)

    score = session.get("individual_score", 0)
    game = session.get("game", "")

    profile.put("total_games", profile.get("total_games") + 1)
    profile.put("total_score", profile.get("total_score") + score)
    profile.put("total_time", profile.get("total_time") + session.get("game_time", 0))
    if score > profile.get("best_score"):
        profile.put("best_score", score)

    per_game = profile.get("_per_game")
    try:
        game_stats = per_game.get(game)
    except KeyError:
        game_stats = HashTable()
        game_stats.put("games", 0)
        game_stats.put("wins", 0)
        per_game.put(game, game_stats)

    game_stats.put("games", game_stats.get("games") + 1)
    if score > 0:
        game_stats.put("wins", game_stats.get("wins") + 1)
    profile.get("win_rate_per_game").put(game, round(game_stats.get("wins") / game_stats.get("games"), 3))

    score_history = profile.get("score_history")
    entry = HashTable()
    entry.put("game", game)
    entry.put("score", score)
    entry.put("timestamp", session.get("timestamp", ""))
    score_history.insert(0, entry)
    if len(score_history) > 50:
        score_history.pop()

def get_profile(username):
    """Return a player's summary profile and recent score history."""

    try:
        profile = _profiles.get(username)
    except KeyError:
        return None
    win_rates = {}
    win_rate_table = profile.get("win_rate_per_game")
    for i in range(win_rate_table.capacity):
        bucket = win_rate_table.table[i]
        for key, value in bucket:
            win_rates[key] = value

    score_history = []
    for entry in profile.get("score_history"):
        score_history.append({
            "game": entry.get("game"),
            "score": entry.get("score"),
            "timestamp": entry.get("timestamp"),
        })

    return {
        "team": profile.get("team"),
        "total_games": profile.get("total_games"),
        "total_score": profile.get("total_score"),
        "best_score": profile.get("best_score"),
        "total_time": profile.get("total_time"),
        "win_rate_per_game": win_rates,
        "score_history": score_history,
    }

def refresh():
    """Apply any new accounts and sessions to the profile snapshot."""

    for username, data in memory.new_accounts().items():
        try:
            _profiles.get(username)
        except KeyError:
            _profiles.put(username, _new_profile(data.get("team", "unknown")))
    for session in memory.new_sessions():
        username = session.get("username")
        if not username:
            continue
        try:
            profile = _profiles.get(username)
        except KeyError:
            profile = _new_profile("unknown")
            _profiles.put(username, profile)

        score = session.get("individual_score", 0)
        game = session.get("game", "")

        profile.put("total_games", profile.get("total_games") + 1)
        profile.put("total_score", profile.get("total_score") + score)
        profile.put("total_time", profile.get("total_time") + session.get("game_time", 0))
        if score > profile.get("best_score"):
            profile.put("best_score", score)

        per_game = profile.get("_per_game")
        try:
            game_stats = per_game.get(game)
        except KeyError:
            game_stats = HashTable()
            game_stats.put("games", 0)
            game_stats.put("wins", 0)
            per_game.put(game, game_stats)

        game_stats.put("games", game_stats.get("games") + 1)
        if score > 0:
            game_stats.put("wins", game_stats.get("wins") + 1)
        profile.get("win_rate_per_game").put(game, round(game_stats.get("wins") / game_stats.get("games"), 3))

        score_history = profile.get("score_history")
        entry = HashTable()
        entry.put("game", game)
        entry.put("score", score)
        entry.put("timestamp", session.get("timestamp", ""))
        score_history.insert(0, entry)
        if len(score_history) > 50:
            score_history.pop()

