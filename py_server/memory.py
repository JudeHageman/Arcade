import json
from pathlib import Path

_data = Path(__file__).parent.parent / "data"

# track how many records have already been loaded
_session_counter = 0
_account_counter = 0
_game_counter = 0

# cached batch from the most recent refresh() call — shared across all modules
_pending_sessions = []
_pending_accounts = {}
_pending_games = {}

# data files
accounts = {}
sessions = []
games = {}

def _read(filename):
    """Read NDJSON records from a data file and return them as a list."""

    path = _data / filename
    if not path.exists():
        return []
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                lines.append(json.loads(line))
            except Exception:
                pass
    return lines

def load():
    """Load the full in-memory snapshot for accounts, sessions, and games."""

    global accounts, sessions, games, _session_counter, _account_counter, _game_counter

    account_entries = _read("accounts.ndjson")
    accounts = {}
    for entry in account_entries:
        accounts.update(entry)
    _account_counter = len(account_entries)

    sessions = _read("sessions.ndjson")
    _session_counter = len(sessions)

    game_entries = _read("games.ndjson")
    games = {}
    for entry in game_entries:
        games.update(entry)
    _game_counter = len(game_entries)

def refresh():
    """Read any new records from disk and cache them for this request cycle.

    Call this once per query before dispatching to any module. All modules
    read from the same cached batch via new_sessions / new_accounts / new_games,
    so every module sees the same new records regardless of call order.
    """

    global sessions, accounts, games
    global _session_counter, _account_counter, _game_counter
    global _pending_sessions, _pending_accounts, _pending_games

    all_sessions = _read("sessions.ndjson")
    _pending_sessions = all_sessions[_session_counter:]
    sessions.extend(_pending_sessions)
    _session_counter = len(all_sessions)

    all_account_entries = _read("accounts.ndjson")
    _pending_accounts = {}
    for entry in all_account_entries[_account_counter:]:
        _pending_accounts.update(entry)
    accounts.update(_pending_accounts)
    _account_counter = len(all_account_entries)

    all_game_entries = _read("games.ndjson")
    _pending_games = {}
    for entry in all_game_entries[_game_counter:]:
        _pending_games.update(entry)
    games.update(_pending_games)
    _game_counter = len(all_game_entries)

def new_sessions():
    """Return the sessions collected during the most recent refresh() call."""
    return _pending_sessions

def new_accounts():
    """Return the accounts collected during the most recent refresh() call."""
    return _pending_accounts

def new_games():
    """Return the games collected during the most recent refresh() call."""
    return _pending_games

load()