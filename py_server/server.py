# used for async process management and the WebSocket server
import asyncio

# data modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "data_structures"))

# modules for query responses
import games as games_module
import leaderboards as leaderboards_module
import profile as profile_module
import match_history as match_history_module
import player_search as player_search_module
import memory

# custom data structures for server state
from hash_table import HashTable
from dynamic_array import ArrayList

# used to connect to the Python server
import websockets

# used for games library, chat history, and live chat messages
import json

# used to store account passwords
import hashlib
from pathlib import Path

# used for timestamps on chat messages
from datetime import datetime

# used for command line arguments to allow custom port
import sys

# allow custom port via command line argument, default to 8000
server_port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8000

# data folder
data_folder = Path(__file__).parent.parent / "data"

# account storage
accounts_file = data_folder / "accounts.ndjson"

# chat log
chats_file = data_folder / "chats.ndjson"

# team chat log
team_chats_file = data_folder / "team_chats.ndjson"

# sessions log (all game sessions for all users)
sessions_file = data_folder / "sessions.ndjson"

# games library
games_file = data_folder / "games.ndjson"

# server state
connected_clients = HashTable()
game_chats = HashTable()
recent_chats = HashTable()
team_chats = HashTable()
recent_team_chats = HashTable()
accounts = HashTable()

def _load_games():
    """Load games from disk."""
    games = HashTable()
    if not games_file.exists():
        return games
    try:
        with games_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    for game_name, info in entry.items():
                        games.put(game_name, info)
                except Exception:
                    continue
    except Exception:
        pass
    return games

GAMES_LIBRARY = _load_games()

def _load_accounts():
    """Load saved accounts from disk."""
    accounts = HashTable()
    if not accounts_file.exists():
        return accounts
    try:
        with accounts_file.open("r", encoding="utf-8") as file_handle:
            for line in file_handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    for username, data in entry.items():
                        accounts.put(username, data)
                except Exception:
                    continue
    except Exception:
        pass
    return accounts
    
# load accounts on server startup
accounts = _load_accounts()

def _load_chats():
    """Load the last 50 chat messages per game from chats.ndjson"""
    chats = HashTable()
    if not chats_file.exists():
        return chats

    # resolve which games to collect for so we know when to stop early
    known_games = set()
    for i in range(GAMES_LIBRARY.capacity):
        for game_name, _ in GAMES_LIBRARY.table[i]:
            known_games.add(game_name)

    LIMIT = 50
    CHUNK = 64 * 1024  # bytes per backwards read

    # collected[game] = list of entries, most-recent first
    collected = {}

    try:
        with chats_file.open("rb") as f:
            f.seek(0, 2)
            pos = f.tell()
            leftover = b""

            while pos > 0:
                read_size = min(CHUNK, pos)
                pos -= read_size
                f.seek(pos)
                chunk = f.read(read_size) + leftover
                lines = chunk.split(b"\n")
                # first element may be a partial line when not at file start
                if pos > 0:
                    leftover = lines[0]
                    lines = lines[1:]
                else:
                    leftover = b""

                for line in reversed(lines):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        game_name = entry.get("game")
                        if not game_name:
                            continue
                        bucket = collected.setdefault(game_name, [])
                        if len(bucket) < LIMIT:
                            bucket.append({
                                "sender": entry.get("sender", ""),
                                "message": entry.get("message", ""),
                                "timestamp": entry.get("timestamp", "")
                            })
                    except Exception:
                        continue

                # stop once every known game has reached the limit
                if known_games and all(
                    len(collected.get(g, [])) >= LIMIT for g in known_games
                ):
                    break

    except Exception:
        pass

    # reverse back to chronological order and store in the HashTable
    for game_name, messages in collected.items():
        messages.reverse()
        chat_list = ArrayList()
        for msg in messages:
            chat_list.append(msg)
        chats.put(game_name, chat_list)

    return chats

# load chat history on server startup
game_chats = _load_chats()

def _load_team_chats():
    """Load the last 50 team chat messages per team from team_chats.ndjson."""
    
    chats = HashTable()
    if not team_chats_file.exists():
        return chats

    LIMIT = 50
    CHUNK = 64 * 1024
    collected = {}

    try:
        with team_chats_file.open("rb") as f:
            f.seek(0, 2)
            pos = f.tell()
            leftover = b""

            while pos > 0:
                read_size = min(CHUNK, pos)
                pos -= read_size
                f.seek(pos)
                chunk = f.read(read_size) + leftover
                lines = chunk.split(b"\n")
                if pos > 0:
                    leftover = lines[0]
                    lines = lines[1:]
                else:
                    leftover = b""

                for line in reversed(lines):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        team_name = entry.get("team")
                        if not team_name:
                            continue
                        bucket = collected.setdefault(team_name, [])
                        if len(bucket) < LIMIT:
                            bucket.append({
                                "sender": entry.get("sender", ""),
                                "message": entry.get("message", ""),
                                "timestamp": entry.get("timestamp", "")
                            })
                    except Exception:
                        continue

    except Exception:
        pass

    for team_name, messages in collected.items():
        messages.reverse()
        chat_list = ArrayList()
        for msg in messages:
            chat_list.append(msg)
        chats.put(team_name, chat_list)

    return chats

# load team chat history on server startup
team_chats = _load_team_chats()

def _chats_to_dict(chats_ht):
    """Convert the chat HashTable to a plain dict for JSON serialization."""
    result = {}
    for i in range(chats_ht.capacity):
        for game_name, chat_list in chats_ht.table[i]:
            messages = []
            for j in range(len(chat_list)):
                messages.append(chat_list[j])
            result[game_name] = messages
    return result

def _append_account(username, account_data):
    """Append a new account record to accounts.ndjson."""
    try:
        with accounts_file.open("a", encoding="utf-8") as file_handle:
            file_handle.write(json.dumps({username: account_data}) + "\n")
    except Exception:
        pass

def _append_session(entry):
    try:
        # sessions_file 경로가 data/sessions.ndjson 을 정확히 가리키는지 확인!
        with sessions_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"--- ❌ [FILE ERROR] 장부 쓰기 실패: {e} ---")

def authenticate_account(username, password):
    """Check login credentials without creating the account."""
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return 'invalid'

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    try:
        account = accounts.get(username)
    except KeyError:
        return 'new'

    if account.get("password") != password_hash:
        return 'invalid'

    return 'existing'


def create_account(username, password_hash, team="default"):
    """Persist a new account with its pre-hashed password and team."""
    account_data = {"password": password_hash, "team": team}
    accounts.put(username, account_data)
    _append_account(username, account_data)

async def check_game_server(host, port):
    """Check if a game server is running on the given host and port."""
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


async def send_status():
<<<<<<< HEAD
    """Broadcast the current status of all games and chats to connected clients."""
    global recent_chats, recent_team_chats
=======
    """모든 클라이언트에게 실시간 게임 상태, 채팅, 리더보드를 방송함"""
    global recent_chats
>>>>>>> 58400efae7f884f59d874e44e2d6211ceff6dc65

    while True:
        try:
            # 1. [가장 중요] 파일(sessions.ndjson)에서 새로운 점수 줄을 읽어오기
            # 이게 없으면 새 아이디로 점수를 내도 서버는 옛날 데이터만 기억해!
            memory.refresh()
            leaderboards_module.refresh()
            top_scores = leaderboards_module.get_leaderboard("Immortal Tree")
            # 2. 게임 서버 상태 체크 (네 HashTable 구조 활용)
            games_status = {}
            for i in range(GAMES_LIBRARY.capacity):
                for game_name, game_info in GAMES_LIBRARY.table[i]:
                    port = game_info["port"]
                    connected = await check_game_server("127.0.0.1", port)
                    games_status[game_name] = {
                        "port": port,
                        "path": game_info["path"],
                        "status": "connected" if connected else "disconnected",
                        "resonance": game_info.get("resonance", False)
                    }

            # 3. 인증된 유저 수 계산 및 클라이언트 리스트 생성
            auth_count = 0
            clients_to_send = ArrayList() # 네가 만든 ArrayList 사용
            for i in range(connected_clients.capacity):
                for client, state in connected_clients.table[i]:
                    if state.get("authenticated"):
                        auth_count += 1
                        clients_to_send.append(client)

            # 4. 최신 리더보드 가져오기
            # 게임 이름 "Immortal Tree"가 로그의 이름과 일치해야 함
            top_scores = leaderboards_module.get_leaderboard("Immortal Tree", top_n=10)

            # 5. 전송할 메시지 구성 (JSON)
            message = json.dumps({
                "type": "global",
                "clients": auth_count,
                "games": games_status,
                "recent_chats": _chats_to_dict(recent_chats),
                "leaderboard": top_scores
            })

            # 6. 실제로 모든 유저에게 보내기 (비동기 처리)
            if len(clients_to_send) > 0:
                # 모든 유저에게 동시에 전송 시도
                send_tasks = [clients_to_send[j].send(message) for j in range(len(clients_to_send))]
                results = await asyncio.gather(*send_tasks, return_exceptions=True)

                # 전송 중 에러(연결 끊김) 난 클라이언트 정리
                for j in range(len(results)):
                    if isinstance(results[j], Exception):
                        try:
                            connected_clients.remove(clients_to_send[j])
                        except KeyError:
                            pass

<<<<<<< HEAD
            # send each authenticated client their own team's recent messages
            for i in range(connected_clients.capacity):
                for client, state in connected_clients.table[i]:
                    if not state.get("authenticated"):
                        continue
                    username = state.get("username") or ""
                    try:
                        team = accounts.get(username).get("team", "default")
                    except KeyError:
                        team = "default"
                    try:
                        recent = recent_team_chats.get(team)
                        msgs = [recent[k] for k in range(len(recent))]
                    except KeyError:
                        msgs = []
                    if msgs:
                        try:
                            await client.send(json.dumps({"type": "team_chat_update", "messages": msgs}))
                        except Exception:
                            pass

=======
            # 실시간 채팅 목록 비우기 및 2초 대기
>>>>>>> 58400efae7f884f59d874e44e2d6211ceff6dc65
            recent_chats = HashTable()
            recent_team_chats = HashTable()
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"--- BROADCAST ERROR: {e} ---")
            await asyncio.sleep(2)
            
async def handle_client(client):
    """Handle a new client connection and listen for messages from that client."""
    connected_clients.put(client, {"authenticated": False, "username": None, "pending_hash": None})

    try:
        await client.send(json.dumps({"type": "auth_required", "message": "Login required."}))
    except Exception:
        try:
            connected_clients.remove(client)
        except KeyError:
            pass
        return

    try:
        async for payload in client:
            try:
                data = json.loads(payload)
                try:
                    client_state = connected_clients.get(client)
                except KeyError:
                    continue

                action = data.get("action")

                if action == "score":
                    player = client_state.get("username") or "Unknown"
                    game_name = data.get("game", "")
                    score = data.get("individual_score", 0)

                    # 1단계: 메시지 도착 확인
                    print(f"--- [DEBUG 1] 점수 신호 도착: {player}님이 {game_name}에서 {score}점 획득!")

                    # 2단계: HashTable에서 게임 찾기 (in 대신 get 사용)
                    try:
                        game_info = GAMES_LIBRARY.get(game_name)
                        print(f"--- [DEBUG 2] 도서관에서 게임 정보 찾음: {game_name}")
                    except KeyError:
                        print(f"--- [DEBUG 2 ERROR] '{game_name}'은 도서관에 없는 이름이야! (대소문자 확인해봐)")
                        continue

                    # 3단계: Resonance 설정 확인
                    if game_info and game_info.get("resonance"):
                        print(f"--- [DEBUG 3] Resonance 게임 확인 완료. 장부에 적기 시작!")
                        
                        session_entry = {
                            "username": player,
                            "game": game_name,
                            "individual_score": score,
                            "team": data.get("team", "default"),
                            "team_score": data.get("team_score", 0),
                            "game_time": data.get("game_time", 0),
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # 4단계: 실제 파일 쓰기
                        try:
                            _append_session(session_entry)
                            # ⭐ 이 로그가 떠야 리더보드에 이름이 올라가!
                            print(f"--- ✅ [SUCCESS] 장부 기록 완료: {player} ({score}점) ---")
                        except Exception as e:
                            print(f"--- [DEBUG 4 ERROR] 파일 쓰기 실패: {e}")
                    else:
                        print(f"--- [DEBUG 3 ERROR] '{game_name}'의 resonance 설정이 False이거나 정보가 없어.")
                    continue
                
                if action == "login":
                    username = data.get("username", "").strip()
                    password = data.get("password", "")
                    result = authenticate_account(username, password)

                    # server.py 의 handle_client 함수 내부 - "login" 처리 부분
                    if result == "existing":
                        client_state["authenticated"] = True
                        client_state["username"] = username
<<<<<<< HEAD
                        team = accounts.get(username).get("team", "default")
                        try:
                            tc = team_chats.get(team)
                            tc_history = [tc[k] for k in range(len(tc))]
                        except KeyError:
                            tc_history = []
                        initial_payload = {
                            "type": "initial",
                            "username": username,
                            "team": team,
                            "chat_history": _chats_to_dict(game_chats),
                            "team_chat_history": tc_history
=======
                        
                        # [수정] 매치 히스토리 가져오기
                        match_history_module.refresh() # 최신 파일 읽기
                        user_matches = match_history_module.get_match_history(username)

                        initial_payload = {
                            "type": "initial",
                            "username": username,
                            "team": accounts.get(username).get("team", "default"),
                            "chat_history": _chats_to_dict(game_chats),
                            "match_history": user_matches  # ✅ 이 줄이 빠져있었어!
>>>>>>> 58400efae7f884f59d874e44e2d6211ceff6dc65
                        }
                        await client.send(json.dumps(initial_payload))
                       
                    elif result == "new":
                        password_hash = hashlib.sha256(password.strip().encode("utf-8")).hexdigest()
                        client_state["pending_username"] = username
                        client_state["pending_hash"] = password_hash
                        await client.send(json.dumps({"type": "select_team"}))
                    continue

                if not client_state.get("authenticated"):
                    if action == "select_team":
                        pending_username = client_state.get("pending_username")
                        pending_hash = client_state.get("pending_hash")
                        team = data.get("team", "")

                        if pending_username and pending_hash and team:
                            create_account(pending_username, pending_hash, team)
                            client_state["authenticated"] = True
                            client_state["username"] = pending_username
                            client_state["pending_username"] = None
                            client_state["pending_hash"] = None
                            try:
                                tc = team_chats.get(team)
                                tc_history = [tc[k] for k in range(len(tc))]
                            except KeyError:
                                tc_history = []
                            initial_payload = {
                                "type": "initial",
                                "username": pending_username,
                                "team": team,
                                "chat_history": _chats_to_dict(game_chats),
                                "team_chat_history": tc_history
                            }
                            await client.send(json.dumps(initial_payload))
                    continue

                if action == "query":
                    query_type = data.get("query")
                    username = client_state.get("username") or ""

                    memory.refresh()
                    profile_module.refresh()
                    leaderboards_module.refresh()
                    match_history_module.refresh()
                    player_search_module.refresh()
                    games_module.refresh()

                    if query_type == "profile":
                        target = data.get("username", username)
                        result = profile_module.get_profile(target)
                        await client.send(json.dumps({"type": "profile", "data": result}))

                    elif query_type == "leaderboard":
                        game_name = data.get("game", "")
                        sort_by = data.get("sort_by", "best_score")
                        top_n = data.get("top_n", 10)
                        rows = leaderboards_module.get_leaderboard(game_name, top_n=top_n, sort_by=sort_by)
                        rank = leaderboards_module.get_own_rank(game_name, username, sort_by=sort_by)
                        await client.send(json.dumps({"type": "leaderboard", "game": game_name, "sort_by": sort_by, "rows": rows, "own_rank": rank}))

                    elif query_type == "match_history":
                        target = data.get("username", username)
                        game_filter = data.get("game", None)
                        date_from = data.get("date_from", None)
                        date_to = data.get("date_to", None)
                        rows = match_history_module.get_match_history(target, game=game_filter, date_from=date_from, date_to=date_to)
                        await client.send(json.dumps({"type": "match_history", "data": rows}))

                    elif query_type == "player_search":
                        prefix = data.get("prefix", "")
                        results = player_search_module.search_players(prefix) if prefix else []
                        await client.send(json.dumps({"type": "player_search", "results": results}))

                    elif query_type == "player_profile":
                        target = data.get("username", "")
                        result = player_search_module.get_player(target)
                        await client.send(json.dumps({"type": "player_profile", "data": result}))

                    elif query_type == "games_catalog":
                        sort_by = data.get("sort_by", "most_played")
                        rows = games_module.get_all_games_sorted(sort_by)
                        await client.send(json.dumps({"type": "games_catalog", "rows": rows}))

                    continue

                if action == "team_chat":
                    message = data.get("message", "").strip()
                    sender = client_state.get("username") or "Unknown"

                    if message and sender:
                        try:
                            team = accounts.get(sender).get("team", "default")
                        except KeyError:
                            team = "default"

                        try:
                            chat_list = team_chats.get(team)
                        except KeyError:
                            chat_list = ArrayList()
                            team_chats.put(team, chat_list)
                        try:
                            recent_list = recent_team_chats.get(team)
                        except KeyError:
                            recent_list = ArrayList()
                            recent_team_chats.put(team, recent_list)

                        chat_entry = {
                            "sender": sender,
                            "message": message,
                            "timestamp": datetime.now().isoformat()
                        }
                        chat_list.append(chat_entry)
                        recent_list.append(chat_entry)
                        if len(chat_list) > 50:
                            chat_list.pop(0)

                        try:
                            with team_chats_file.open("a", encoding="utf-8") as f:
                                f.write(json.dumps({"team": team, **chat_entry}) + "\n")
                        except Exception:
                            pass

                if action == "chat":
                    game_name = data.get("game")
                    message = data.get("message", "").strip()
                    sender = client_state.get("username") or "Unknown"

                    if game_name and message:
                        try:
                            chat_list = game_chats.get(game_name)
                        except KeyError:
                            chat_list = ArrayList()
                            game_chats.put(game_name, chat_list)
                        try:
                            recent_list = recent_chats.get(game_name)
                        except KeyError:
                            recent_list = ArrayList()
                            recent_chats.put(game_name, recent_list)

                        chat_entry = {
                            "sender": sender,
                            "message": message,
                            "timestamp": datetime.now().isoformat()
                        }
                        chat_list.append(chat_entry)
                        recent_list.append(chat_entry)
                        if len(chat_list) > 50:
                            chat_list.pop(0)

                        try:
                            with chats_file.open("a", encoding="utf-8") as f:
                                f.write(json.dumps({"game": game_name, **chat_entry}) + "\n")
                        except Exception:
                            pass

            except json.JSONDecodeError:
                pass
                
    except websockets.exceptions.ConnectionClosed:
        try:
            connected_clients.remove(client)
        except KeyError:
            pass
    finally:
        try:
            connected_clients.remove(client)
        except KeyError:
            pass

async def run_server():
    """Start the WebSocket server and periodically send status updates to clients."""
    server = await websockets.serve(handle_client, "127.0.0.1", server_port)
    asyncio.create_task(send_status())
    
    await asyncio.Future()

# entry point to start the server
if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass
