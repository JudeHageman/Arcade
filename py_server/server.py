# used for async process management and the WebSocket server
import asyncio

# used to connect to the Python server
import websockets

# used for games library, chat history, and live chat messages
import json

# used for timestamps on chat messages
from datetime import datetime

# used for command line arguments to allow custom port
import sys

# allow custom port via command line argument, default to 8000
server_port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8000

# server state
connected_clients = set()
current_games_status = {}
game_chats = {}

# library of games with their ports and paths
GAMES_LIBRARY = {
    "Game 1": {"port": 8080, "path": "game_1"},
    "Game 2": {"port": 8081, "path": "game_2"},
    "Game 3": {"port": 8082, "path": "game_3"}
}

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
            message = json.dumps({
                "clients": len(connected_clients),
                "games": games_status,
                "chat_history": game_chats
            })

            print(f"\n[STATUS] {message}")

            if connected_clients:
                clients = list(connected_clients)
                results = await asyncio.gather(*(client.send(message) for client in clients), return_exceptions=True)

                disconnected = {client for client, result in zip(clients, results) if isinstance(result, Exception)}
                connected_clients.difference_update(disconnected)

            await asyncio.sleep(2)
            
        except Exception:
            await asyncio.sleep(2)

async def handle_client(client):
    """Handle a new client connection and listen for messages from that client."""
    connected_clients.add(client)

    try:
        async for payload in client:
            try:
                data = json.loads(payload)
                
                if data.get("type") == "chat":
                    game_name = data.get("game")
                    message = data.get("message", "").strip()
                    sender = data.get("sender", "Unknown")
                    
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
        if client in connected_clients:
            connected_clients.remove(client)

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
