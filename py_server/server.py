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

# sessions log (all game sessions for all users)
sessions_file = data_folder / "sessions.ndjson"

# games library
games_file = data_folder / "games.ndjson"

# server state
connected_clients = HashTable()
game_chats = HashTable()
recent_chats = HashTable()
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
    """Load persisted chat history from chats.ndjson into game_chats."""
    chats = HashTable()
    if not chats_file.exists():
        return chats
    try:
        with chats_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    game_name = entry.get("game")
                    if not game_name:
                        continue
                    try:
                        chat_list = chats.get(game_name)
                    except KeyError:
                        chat_list = ArrayList()
                        chats.put(game_name, chat_list)
                    chat_list.append({
                        "sender": entry.get("sender", ""),
                        "message": entry.get("message", ""),
                        "timestamp": entry.get("timestamp", "")
                    })
                except Exception:
                    continue
    except Exception:
        pass
    # keep only the last 50 messages per game
    for i in range(chats.capacity):
        for _, chat_list in chats.table[i]:
            while len(chat_list) > 50:
                chat_list.pop(0)
    return chats

# load chat history on server startup
game_chats = _load_chats()

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
    """Append a session record to sessions.ndjson."""
    try:
        with sessions_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

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
    """Broadcast the current status of all games and chats to connected clients."""
    global recent_chats

    while True:
        try:
            games_status = {}
            for i in range(GAMES_LIBRARY.capacity):
                for game_name, game_info in GAMES_LIBRARY.table[i]:
                    port = game_info["port"]
                    path = game_info["path"]
                    resonance = game_info.get("resonance", False)
                    connected = await check_game_server("127.0.0.1", port)
                    games_status[game_name] = {
                        "port": port,
                        "path": path,
                        "status": "connected" if connected else "disconnected",
                        "resonance": resonance
                    }

            authenticated_clients = 0
            for i in range(connected_clients.capacity):
                for _, state in connected_clients.table[i]:
                    if state.get("authenticated"):
                        authenticated_clients += 1

            message = json.dumps({
                "type": "global",
                "clients": authenticated_clients,
                "games": games_status,
                "recent_chats": _chats_to_dict(recent_chats)
            })

            clients = ArrayList()
            for i in range(connected_clients.capacity):
                for client, state in connected_clients.table[i]:
                    if state.get("authenticated"):
                        clients.append(client)

            if len(clients):
                results = await asyncio.gather(
                    *(clients[j].send(message) for j in range(len(clients))),
                    return_exceptions=True
                )

                disconnected = ArrayList()
                for j in range(len(clients)):
                    if isinstance(results[j], Exception):
                        disconnected.append(clients[j])
                for j in range(len(disconnected)):
                    try:
                        connected_clients.remove(disconnected[j])
                    except KeyError:
                        pass

            recent_chats = HashTable()
            await asyncio.sleep(2)
            
        except Exception:
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
                    player = client_state.get("username") or ""
                    game_name = data.get("game", "")
                    individual_score = data.get("individual_score", 0)
                    team = data.get("team", "")
                    team_score = data.get("team_score", 0)
                    game_time = data.get("game_time", 0)

                    # only process scores for games that support resonance
                    if game_name in GAMES_LIBRARY and GAMES_LIBRARY.get(game_name).get("resonance"):
                        if player and game_name:
                            session_entry = {
                                "username": player,
                                "game": game_name,
                                "individual_score": individual_score,
                                "team": team,
                                "team_score": team_score,
                                "game_time": game_time,
                                "timestamp": datetime.now().isoformat()
                            }
                            _append_session(session_entry)
                    continue

                if action == "login":
                    username = data.get("username", "").strip()
                    password = data.get("password", "")
                    result = authenticate_account(username, password)

                    if result == "existing":
                        client_state["authenticated"] = True
                        client_state["username"] = username
                        team = accounts.get(username).get("team", "default")
                        initial_payload = {
                            "type": "initial",
                            "username": username,
                            "team": team,
                            "chat_history": _chats_to_dict(game_chats)
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
                            initial_payload = {
                                "type": "initial",
                                "username": pending_username,
                                "team": team,
                                "chat_history": _chats_to_dict(game_chats)
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
