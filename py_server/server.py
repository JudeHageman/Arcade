# used for async process management and the WebSocket server
import asyncio

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
connected_clients = {}
current_games_status = {}
game_chats = {}
recent_chats = {}
accounts = {}

def load_games():
    """Load games from disk."""
    if not games_file.exists():
        return {}
    games = {}
    try:
        with games_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    games.update(entry)
                except Exception:
                    continue
    except Exception:
        pass
    return games

GAMES_LIBRARY = load_games()

def load_accounts():
    """Load saved accounts from disk."""
    if not accounts_file.exists():
        return {}
    accounts = {}
    try:
        with accounts_file.open("r", encoding="utf-8") as file_handle:
            for line in file_handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    accounts.update(entry)
                except Exception:
                    continue
    except Exception:
        pass
    return accounts
    
# load accounts on server startup
accounts = load_accounts()

def load_chats():
    """Load persisted chat history from chats.ndjson into game_chats."""
    if not chats_file.exists():
        return {}
    chats = {}
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
                    chats.setdefault(game_name, []).append({
                        "sender": entry.get("sender", ""),
                        "message": entry.get("message", ""),
                        "timestamp": entry.get("timestamp", "")
                    })
                except Exception:
                    continue
    except Exception:
        pass
    # keep only the last 50 messages per game
    for game_name in chats:
        chats[game_name] = chats[game_name][-50:]
    return chats

# load chat history on server startup
game_chats = load_chats()

def append_account(username, account_data):
    """Append a new account record to accounts.ndjson."""
    try:
        with accounts_file.open("a", encoding="utf-8") as file_handle:
            file_handle.write(json.dumps({username: account_data}) + "\n")
    except Exception:
        pass

def append_session(entry):
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
    account = accounts.get(username)

    if account is None:
        return 'new'

    if account.get("password") != password_hash:
        return 'invalid'

    return 'existing'


def create_account(username, password_hash, team="default"):
    """Persist a new account with its pre-hashed password and team."""
    account_data = {"password": password_hash, "team": team}
    accounts[username] = account_data
    append_account(username, account_data)

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
    global current_games_status, recent_chats

    while True:
        try:
            games_status = {}
            for game_name, game_info in GAMES_LIBRARY.items():
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

            current_games_status = games_status

            authenticated_clients = 0
            for state in connected_clients.values():
                if state.get("authenticated"):
                    authenticated_clients += 1

            message = json.dumps({
                "type": "global",
                "clients": authenticated_clients,
                "games": games_status,
                "recent_chats": recent_chats
            })

            clients = [client for client, state in connected_clients.items() if state.get("authenticated")]
            if clients:
                results = await asyncio.gather(*(client.send(message) for client in clients), return_exceptions=True)

                disconnected = {client for client, result in zip(clients, results) if isinstance(result, Exception)}
                for client in disconnected:
                    connected_clients.pop(client, None)

            recent_chats = {}
            await asyncio.sleep(2)
            
        except Exception:
            await asyncio.sleep(2)

async def handle_client(client):
    """Handle a new client connection and listen for messages from that client."""
    connected_clients[client] = {"authenticated": False, "username": None, "pending_hash": None}

    try:
        await client.send(json.dumps({"type": "auth_required", "message": "Login required."}))
    except Exception:
        connected_clients.pop(client, None)
        return

    try:
        async for payload in client:
            try:
                data = json.loads(payload)
                client_state = connected_clients.get(client)
                if client_state is None:
                    continue

                if data.get("type") == "user":
                    action = data.get("action")

                    if action == "score":
                        player = client_state.get("username") or ""
                        game_name = data.get("game", "")
                        individual_score = data.get("individual_score", 0)
                        team = data.get("team", "")
                        team_score = data.get("team_score", 0)
                        game_time = data.get("game_time", 0)

                        # Only process scores for games that support resonance
                        if game_name in GAMES_LIBRARY and GAMES_LIBRARY[game_name].get("resonance"):
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
                                append_session(session_entry)
                        continue

                    if action == "login":
                        username = data.get("username", "").strip()
                        password = data.get("password", "")
                        result = authenticate_account(username, password)

                        if result == "existing":
                            client_state["authenticated"] = True
                            client_state["username"] = username
                            team = accounts[username].get("team", "default")
                            initial_payload = {
                                "type": "initial",
                                "username": username,
                                "team": team,
                                "chat_history": game_chats
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
                                    "chat_history": game_chats
                                }
                                await client.send(json.dumps(initial_payload))
                        continue

                    if action == "chat":
                        game_name = data.get("game")
                        message = data.get("message", "").strip()
                        sender = client_state.get("username") or "Unknown"

                        if game_name and message:
                            if game_name not in game_chats:
                                game_chats[game_name] = []
                            if game_name not in recent_chats:
                                recent_chats[game_name] = []
                            
                            chat_entry = {
                                "sender": sender,
                                "message": message,
                                "timestamp": datetime.now().isoformat()
                            }
                            game_chats[game_name].append(chat_entry)
                            recent_chats[game_name].append(chat_entry)
                            if len(game_chats[game_name]) > 50:
                                game_chats[game_name].pop(0)

                            try:
                                with chats_file.open("a", encoding="utf-8") as f:
                                    f.write(json.dumps({"game": game_name, **chat_entry}) + "\n")
                            except Exception:
                                pass

            except json.JSONDecodeError:
                pass
                
    except websockets.exceptions.ConnectionClosed:
        connected_clients.pop(client, None)
    finally:
        connected_clients.pop(client, None)

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
