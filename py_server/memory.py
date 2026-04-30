import json
from pathlib import Path

_data = Path(__file__).parent.parent / "data"

<<<<<<< HEAD
# track how far into each file we have already consumed
_session_offset = 0
_account_offset = 0
_game_offset = 0
=======
# 카운터 및 캐시 변수
_session_counter = 0
_account_counter = 0
_game_counter = 0
>>>>>>> 58400efae7f884f59d874e44e2d6211ceff6dc65

_pending_sessions = []
_pending_accounts = {}
_pending_games = {}

# 전체 데이터 스냅샷
accounts = {}
sessions = []
games = {}

<<<<<<< HEAD
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
=======
def _read(filename):
    """NDJSON 파일을 읽어서 리스트로 반환 (에러 발생 시 로그 출력)"""
    path = _data / filename
    if not path.exists():
        return []
    
    lines = []
    # read_text 대신 안전하게 파일을 직접 열어서 한 줄씩 읽기
    try:
        with path.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line: continue
                try:
                    lines.append(json.loads(line))
                except Exception as e:
                    # JSON 형식이 깨진 줄이 있으면 어디인지 알려줌
                    print(f"--- MEMORY ERROR: JSON parse failed at {filename} line {i+1}: {e} ---")
    except Exception as e:
        print(f"--- MEMORY ERROR: Could not read {filename}: {e} ---")
        
    return lines

def load():
    """서버 시작 시 전체 데이터를 한 번 로드"""
    global accounts, sessions, games, _session_counter, _account_counter, _game_counter
>>>>>>> 58400efae7f884f59d874e44e2d6211ceff6dc65

    account_entries, _account_offset = _read_from("accounts.ndjson", 0)
    accounts = {}
    for entry in account_entries:
        accounts.update(entry)

    sessions, _session_offset = _read_from("sessions.ndjson", 0)

    game_entries, _game_offset = _read_from("games.ndjson", 0)
    games = {}
    for entry in game_entries:
        games.update(entry)
<<<<<<< HEAD

def refresh():
    """Read any new records from disk and cache them for this request cycle."""

=======
    _game_counter = len(game_entries)
    print(f"--- MEMORY: Initial load complete ({_session_counter} sessions) ---")

def refresh():
    """새로운 레코드가 있는지 확인하고 캐시 업데이트"""
>>>>>>> 58400efae7f884f59d874e44e2d6211ceff6dc65
    global sessions, accounts, games
    global _session_offset, _account_offset, _game_offset
    global _pending_sessions, _pending_accounts, _pending_games

<<<<<<< HEAD
    _pending_sessions, _session_offset = _read_from("sessions.ndjson", _session_offset)
    sessions.extend(_pending_sessions)

    new_account_entries, _account_offset = _read_from("accounts.ndjson", _account_offset)
    _pending_accounts = {}
    for entry in new_account_entries:
        _pending_accounts.update(entry)
    accounts.update(_pending_accounts)

    new_game_entries, _game_offset = _read_from("games.ndjson", _game_offset)
=======
    # 1. 세션 새로고침
    all_sessions = _read("sessions.ndjson")
    _pending_sessions = all_sessions[_session_counter:]
    
    if _pending_sessions:
        # ✅ 여기에 로그가 찍혀야 12점이 서버 메모리에 들어온 거야!
        print(f"--- MEMORY DEBUG: Found {len(_pending_sessions)} new sessions! ---")
        sessions.extend(_pending_sessions)
        _session_counter = len(all_sessions)

    # 2. 계정 새로고침
    all_account_entries = _read("accounts.ndjson")
    _pending_accounts = {}
    new_acc_count = 0
    for entry in all_account_entries[_account_counter:]:
        _pending_accounts.update(entry)
        new_acc_count += 1
    
    if _pending_accounts:
        accounts.update(_pending_accounts)
        _account_counter = len(all_account_entries)

    # 3. 게임 목록 새로고침
    all_game_entries = _read("games.ndjson")
>>>>>>> 58400efae7f884f59d874e44e2d6211ceff6dc65
    _pending_games = {}
    for entry in new_game_entries:
        _pending_games.update(entry)
<<<<<<< HEAD
    games.update(_pending_games)
=======
    
    if _pending_games:
        games.update(_pending_games)
        _game_counter = len(all_game_entries)
>>>>>>> 58400efae7f884f59d874e44e2d6211ceff6dc65

# 나머지 new_sessions 등 함수는 그대로 유지
def new_sessions(): return _pending_sessions
def new_accounts(): return _pending_accounts
def new_games(): return _pending_games

load()