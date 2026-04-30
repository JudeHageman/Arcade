import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "data_structures"))

# dynamic array used to filter match history results
from dynamic_array import ArrayList

# linked list stores each player's session history
from linked_list import LinkedList

# custom hash table for player histories
from hash_table import HashTable

# shared account and session data
import memory

# history lists keyed by username
_histories = HashTable()

def _make_session_record(session):
    """Build the session record stored inside each player's history."""

    record = HashTable()
    record.put("game", session.get("game", ""))
    record.put("individual_score", session.get("individual_score", 0))
    record.put("team_score", session.get("team_score", 0))
    record.put("game_time", session.get("game_time", 0))
    record.put("timestamp", session.get("timestamp", ""))
    return record

# load the initial match histories from the session
for session in memory.sessions:
    username = session.get("username")
    if not username:
        continue
    try:
        history = _histories.get(username)
    except KeyError:
        history = LinkedList()
        _histories.put(username, history)
    history.add_last(_make_session_record(session))


def get_match_history(username, game=None, date_from=None, date_to=None, outcome=None):
    """Return a player's match history filtered by game, date, or outcome."""

    try:
        history = _histories.get(username)
    except KeyError:
        return []

    sessions = ArrayList()
    node = history.head
    while node:
        sessions.append(node.value)
        node = node.next
    filtered = ArrayList()
    index = len(sessions) - 1
    while index >= 0:
        entry = sessions[index]
        if game and entry.get("game") != game:
            index -= 1
            continue
        if date_from and entry.get("timestamp") < date_from:
            index -= 1
            continue
        if date_to and entry.get("timestamp") > date_to:
            index -= 1
            continue
        if outcome == "positive" and entry.get("individual_score") <= 0:
            index -= 1
            continue
        if outcome == "zero" and entry.get("individual_score") != 0:
            index -= 1
            continue
        filtered.append(entry)
        index -= 1

    output = []
    for entry in filtered:
        output.append({
            "game": entry.get("game"),
            "individual_score": entry.get("individual_score"),
            "team_score": entry.get("team_score"),
            "game_time": entry.get("game_time"),
            "timestamp": entry.get("timestamp"),
        })
    return output

def refresh():
    """Append any new sessions to the stored match histories."""

    for session in memory.new_sessions():
        username = session.get("username")
        if not username:
            continue
        try:
            history = _histories.get(username)
        except KeyError:
            history = LinkedList()
            _histories.put(username, history)
        history.add_last(_make_session_record(session))

