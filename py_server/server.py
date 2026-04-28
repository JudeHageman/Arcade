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

# account storage
accounts_file = Path(__file__).with_name("accounts.json")

# server state
connected_clients = {}
current_games_status = {}
game_chats = {}
accounts = {}

# library of games with their ports and paths
GAMES_LIBRARY = {
    "Immortal Tree": {"port": 8080, "path": "immortal_tree"},
    "Game 2": {"port": 8081, "path": "game_2"},
    "Game 3": {"port": 8082, "path": "game_3"}
}

def load_accounts():
    """Load saved accounts from disk."""
    if not accounts_file.exists():
        return {}

    try:
        with accounts_file.open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    
# load accounts on server startup
accounts = load_accounts()

def save_accounts():
    """Save accounts to file."""
    try:
        with accounts_file.open("w", encoding="utf-8") as file_handle:
            json.dump(accounts, file_handle, indent=2)
    except Exception:
        pass

def authenticate_account(username, password):
    """Create a new account or verify an existing one."""
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return False

    account = accounts.get(username)
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    if account is None:
        accounts[username] = {
            "password": password_hash
        }
        save_accounts()
        return True

    if account.get("password") != password_hash:
        return False

    return True

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
    global current_games_status

    while True:
        try:
            games_status = {}
            for game_name, game_info in GAMES_LIBRARY.items():
                port = game_info["port"]
                path = game_info["path"]
                connected = await check_game_server("127.0.0.1", port)
                games_status[game_name] = {
                    "port": port,
                    "path": path,
                    "status": "connected" if connected else "disconnected"
                }

            current_games_status = games_status

            authenticated_clients = 0
            for state in connected_clients.values():
                if state.get("authenticated"):
                    authenticated_clients += 1

            message = json.dumps({
                "clients": authenticated_clients,
                "games": games_status,
                "chat_history": game_chats
            })

            print(f"\n[STATUS] {message}")

            clients = [client for client, state in connected_clients.items() if state.get("authenticated")]
            if clients:
                results = await asyncio.gather(*(client.send(message) for client in clients), return_exceptions=True)

                disconnected = {client for client, result in zip(clients, results) if isinstance(result, Exception)}
                for client in disconnected:
                    connected_clients.pop(client, None)

            await asyncio.sleep(2)
            
        except Exception:
            await asyncio.sleep(2)

async def handle_client(client):
    """Handle a new client connection and listen for messages from that client."""
    connected_clients[client] = {"authenticated": False, "username": None}

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

                if data.get("type") == "login":
                    username = data.get("username", "")
                    password = data.get("password", "")
                    authenticated = authenticate_account(username, password)

                    if authenticated:
                        client_state["authenticated"] = True
                        client_state["username"] = username.strip()
                        await client.send(json.dumps({"type": "login_success"}))
                    continue

                if not client_state.get("authenticated"):
                    continue
                
                if data.get("type") == "chat":
                    game_name = data.get("game")
                    message = data.get("message", "").strip()
                    sender = client_state.get("username") or data.get("sender", "Unknown")
                    
                    if game_name and message:
                        if game_name not in game_chats:
                            game_chats[game_name] = []

                        chat_entry = {
                            "sender": sender,
                            "message": message,
                            "timestamp": datetime.now().isoformat()
                        }
                        game_chats[game_name].append(chat_entry)
                        if len(game_chats[game_name]) > 50:
                            game_chats[game_name].pop(0)

            except json.JSONDecodeError:
                pass
                
    except websockets.exceptions.ConnectionClosed:
        connected_clients.pop(client, None)
    finally:
        connected_clients.pop(client, None)

async def run_server():
    """Start the WebSocket server and periodically send status updates to clients."""
    server = await websockets.serve(handle_client, "127.0.0.1", server_port)
    print(f"Python server running on ws://127.0.0.1:{server_port}")
    print("Available games:")
    for game_name, game_info in GAMES_LIBRARY.items():
        print(f"  - {game_name} on port {game_info['port']} (path: {game_info['path']})")
    
    asyncio.create_task(send_status())
    
    await asyncio.Future()

# entry point to start the server
if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nServer stopped.")
