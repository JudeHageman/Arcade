import json
from pathlib import Path

_data = Path(__file__).parent.parent / "data"

# track how many records have already been loaded
_session_counter = 0
_account_counter = 0
_game_counter = 0

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

def new_sessions():
    """Append any newly written session records and return them."""

    global sessions, _session_counter
    all_sessions = _read("sessions.ndjson")
    new = all_sessions[_session_counter:]
    sessions.extend(new)
    _session_counter = len(all_sessions)
    return new

def new_accounts():
    """Append any newly written account records and return them."""

    global accounts, _account_counter
    all_entries = _read("accounts.ndjson")
    new = {}
    for entry in all_entries[_account_counter:]:
        new.update(entry)
    accounts.update(new)
    _account_counter = len(all_entries)
    return new

def new_games():
    """Append any newly written game records and return them."""
    
    global games, _game_counter
    all_entries = _read("games.ndjson")
    new = {}
    for entry in all_entries[_game_counter:]:
        new.update(entry)
    games.update(new)
    _game_counter = len(all_entries)
    return new

load()