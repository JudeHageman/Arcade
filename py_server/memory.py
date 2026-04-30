import json
from pathlib import Path

_data = Path(__file__).parent.parent / "data"

# track how far into each file we have already consumed
_session_offset = 0
_account_offset = 0
_game_offset = 0

# cached batch from the most recent refresh() call — shared across all modules
_pending_sessions = []
_pending_accounts = {}
_pending_games = {}

# data files
accounts = {}
sessions = []
games = {}

def _read_from(filename, offset):
    """Read new NDJSON records from a file starting at byte offset."""
    path = _data / filename
    if not path.exists():
        return [], offset
    records = []
    new_offset = offset
    try:
        with path.open("rb") as f:
            f.seek(offset)
            new_bytes = f.read()
            new_offset = offset + len(new_bytes)
        for line in new_bytes.decode("utf-8", errors="replace").splitlines():
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass
    except Exception:
        pass
    return records, new_offset

def load():
    """Load the full in-memory snapshot for accounts, sessions, and games."""

    global accounts, sessions, games, _session_offset, _account_offset, _game_offset

    account_entries, _account_offset = _read_from("accounts.ndjson", 0)
    accounts = {}
    for entry in account_entries:
        accounts.update(entry)

    sessions, _session_offset = _read_from("sessions.ndjson", 0)

    game_entries, _game_offset = _read_from("games.ndjson", 0)
    games = {}
    for entry in game_entries:
        games.update(entry)

def refresh():
    """Read any new records from disk and cache them for this request cycle."""

    global sessions, accounts, games
    global _session_offset, _account_offset, _game_offset
    global _pending_sessions, _pending_accounts, _pending_games

    _pending_sessions, _session_offset = _read_from("sessions.ndjson", _session_offset)
    sessions.extend(_pending_sessions)

    new_account_entries, _account_offset = _read_from("accounts.ndjson", _account_offset)
    _pending_accounts = {}
    for entry in new_account_entries:
        _pending_accounts.update(entry)
    accounts.update(_pending_accounts)

    new_game_entries, _game_offset = _read_from("games.ndjson", _game_offset)
    _pending_games = {}
    for entry in new_game_entries:
        _pending_games.update(entry)
    games.update(_pending_games)

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