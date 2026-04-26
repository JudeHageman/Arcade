# used for the UI
import tkinter as tk

# needed to open the game as a separate process and watch for it to close
import subprocess

# used for command line arguments to allow custom player name
import sys

# used to find the game paths relative to the client script
from pathlib import Path

# used for the async server checks
import asyncio

# used to connect to the Python server
import websockets

# used for background threads to keep the UI running while keeping the websocket open and watching the game process
import threading

# used for games library, chat history, and live chat messages
import json

# websocket connects to a URI, not just a port
server_port = 8000
server_url = f"ws://127.0.0.1:{server_port}"

# allow custom player name via command line argument, default to "Player1"
player_name = sys.argv[1] if len(sys.argv) > 1 else "Player1"

# print connection info
print(f"Connecting to server: {server_url}")
print(f"Player name: {player_name}")

# client state
ws = None
ws_connection = False
ws_loop = None
games_data = {}
loaded_games = {}
game_instance = None
game_buttons = {}
chat_widgets = {}

def clear_game_state():
    """Clear all game and chat state from the client UI and memory."""
    global games_data, loaded_games

    games_data = {}
    loaded_games = {}
    game_buttons.clear()
    chat_widgets.clear()

    for widget in games_frame.winfo_children():
        widget.destroy()

def print_received_games_state():
    """Print the current games data received from the server."""
    games_snapshot = {}

    for game_name, game_info in games_data.items():
        games_snapshot[game_name] = {
            "port": game_info.get("port"),
            "path": game_info.get("path"),
            "status": game_info.get("status"),
            "chat_history": game_info.get("chat_history", [])
        }

    print(f"\n[STATUS] {games_snapshot}")

async def persistent_connection():
    """Maintain a persistent connection to the server, automatically reconnecting if the connection is lost."""
    global ws_connection, ws, ws_loop, games_data
    
    try:
        async with websockets.connect(server_url) as ws_conn:
            ws = ws_conn
            ws_loop = asyncio.get_running_loop()
            ws_connection = True
            window.after(0, update_connection_status)  
            print("\n[STATUS] Server connected")
            
            # listen for messages from the server
            async for payload in ws_conn:
                try:
                    data = json.loads(payload)
                    
                    if data.get("type") == "games_library" or "games" in data:
                        games_data = data.get("games", {})
                        chat_history = data.get("chat_history", {})
                        for game_name, messages in chat_history.items():
                            if game_name in games_data:
                                games_data[game_name]["chat_history"] = messages
                        print_received_games_state()
                        # Schedule UI update on main thread
                        window.after(0, update_games_ui)
                    
                    elif data.get("type") == "chat_history":
                        game_name = data.get("game")
                        messages = data.get("messages", [])
                        print(f"Received chat history for {game_name}: {messages}")
                        if game_name in games_data:
                            games_data[game_name]["chat_history"] = messages
                            print_received_games_state()
                        if game_name in chat_widgets:
                            window.after(0, lambda g=game_name, m=messages: display_chat_history(g, m))
                    
                    elif data.get("type") == "chat":
                        game_name = data.get("game")
                        sender = data.get("sender", "Unknown")
                        message = data.get("message", "")
                        print(f"Received chat for {game_name}: {sender}: {message}")
                        if game_name in games_data:
                            games_data.setdefault(game_name, {}).setdefault("chat_history", []).append({
                                "sender": sender,
                                "message": message
                            })
                            print_received_games_state()
                        if game_name in chat_widgets:
                            window.after(0, lambda g=game_name, s=sender, m=message: add_chat_message(g, s, m))
                        
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {payload}")
                    
    except Exception as e:
        print("\n[STATUS] Not connected to server")
        ws_connection = False
        ws = None
        ws_loop = None
        clear_game_state()
        window.after(0, update_connection_status)

        def retry_connection():
            try:
                asyncio.run(persistent_connection())
            except Exception as retry_error:
                print(f"Reconnect failed: {retry_error}")

        window.after(3000, lambda: threading.Thread(target=retry_connection, daemon=True).start())

def update_connection_status():
    """Update the connection status label in the UI based on the current connection state."""
    if ws_connection:
        connection_label.config(text="Connected to Server")
    else:
        connection_label.config(text="Disconnected from Server")

def add_chat_message(game_name, sender, message):
    """Add a new chat message to the chat display for a specific game."""
    if game_name not in chat_widgets:
        return
    
    chat_display = chat_widgets[game_name].get("display")
    if chat_display:
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"{sender}: {message}\n")
        chat_display.see(tk.END)
        chat_display.config(state=tk.DISABLED)

def display_chat_history(game_name, messages):
    """Display the chat history for a specific game in the chat display."""
    if game_name not in chat_widgets:
        return
    
    chat_display = chat_widgets[game_name].get("display")
    if chat_display:
        chat_display.config(state=tk.NORMAL)
        chat_display.delete(1.0, tk.END)
        for payload in messages:
            sender = payload.get("sender", "Unknown")
            text = payload.get("message", "")
            chat_display.insert(tk.END, f"{sender}: {text}\n")
        chat_display.see(tk.END)
        chat_display.config(state=tk.DISABLED)

def send_chat_message(game_name):
    """Send a chat message for a specific game to the server."""
    global ws, ws_loop
    
    if game_name not in chat_widgets:
        return
    
    chat_input = chat_widgets[game_name].get("input")
    if not chat_input:
        return
    
    message = chat_input.get()
    if not message.strip() or not ws_connection or not ws or not ws_loop:
        return
    
    try:
        payload = json.dumps({
            "type": "chat",
            "game": game_name,
            "sender": player_name,
            "message": message.strip()
        })
        asyncio.run_coroutine_threadsafe(ws.send(payload), ws_loop)
        
        chat_input.delete(0, tk.END)
    except Exception as e:
        print(f"Error sending chat: {e}")

def update_games_ui():
    """Update the games UI based on the current games data received from the server."""
    global loaded_games
    
    if not ws_connection:
        return

    current_game_names = set(games_data.keys())
    loaded_game_names = set(loaded_games.keys())
    
    if not games_data:
        if game_buttons:
            for widget in games_frame.winfo_children():
                widget.destroy()
            game_buttons.clear()
            chat_widgets.clear()
            label = tk.Label(games_frame, text="No games available", font=("Arial", 10))
            label.pack(pady=20)
            loaded_games = {}
        return
    
    if current_game_names != loaded_game_names:
        for widget in games_frame.winfo_children():
            widget.destroy()
        game_buttons.clear()
        chat_widgets.clear()
        
        # create UI for each game
        for game_name, game_info in games_data.items():
            create_game_ui(game_name, game_info)
        
        loaded_games = games_data.copy()
    else:
        # for games that are already loaded, just update their status and chat history
        for game_name, game_info in games_data.items():
            if game_name in game_buttons:
                update_game_status(game_name, game_info)
            if game_name in chat_widgets:
                display_chat_history(game_name, game_info.get("chat_history", []))

def create_game_ui(game_name, game_info):
    """Create the UI elements for a given game."""
    game_container = tk.Frame(games_frame, relief=tk.SUNKEN, bd=1, width=400)
    game_container.pack(pady=10, padx=10)
    
    button_frame = tk.Frame(game_container)
    button_frame.pack(pady=5)
    
    status = game_info.get("status", "unknown")
    display_status = "Disconnected" if status == "disconnected" else "Connected" if status == "connected" else "Unknown"
    
    button = tk.Button(
        button_frame,
        text=f"Launch {game_name}",
        command=lambda name=game_name: run_game(name),
        font=("Arial", 10),
        width=25,
        state=tk.NORMAL if status == "connected" else tk.DISABLED
    )
    button.pack()
    
    status_label = tk.Label(
        button_frame,
        text=f"Status: {display_status}",
        font=("Arial", 9)
    )
    status_label.pack(pady=3)
    
    game_buttons[game_name] = {
        "button": button,
        "status_label": status_label
    }
    
    chat_display = tk.Text(
        game_container,
        height=5,
        width=50,
        state=tk.DISABLED,
        font=("Arial", 8),
        bg="white"
    )
    chat_display.pack(pady=5, padx=5)
    
    chat_input_frame = tk.Frame(game_container)
    chat_input_frame.pack(pady=5, padx=5, fill=tk.X)
    
    chat_input = tk.Entry(chat_input_frame, font=("Arial", 9), width=40)
    chat_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    send_button = tk.Button(
        chat_input_frame,
        text="Send",
        command=lambda g=game_name: send_chat_message(g),
        font=("Arial", 9)
    )
    send_button.pack(side=tk.LEFT, padx=5)
    
    chat_input.bind('<Return>', lambda e, g=game_name: send_chat_message(g))
    
    chat_widgets[game_name] = {
        "display": chat_display,
        "input": chat_input
    }

    history = game_info.get("chat_history", [])
    if history:
        display_chat_history(game_name, history)

def update_game_status(game_name, game_info):
    """Update the status of a given game."""
    if game_name not in game_buttons:
        return
    
    # determine display status based on game_info
    status = game_info.get("status", "unknown")
    display_status = "Disconnected" if status == "disconnected" else "Connected" if status == "connected" else "Unknown"
    
    # update button state and text
    button = game_buttons[game_name]["button"]
    button.config(
        state=tk.NORMAL if status == "connected" else tk.DISABLED,
        text=f"Launch {game_name}"
    )
    
    # update status label
    status_label = game_buttons[game_name]["status_label"]
    status_label.config(text=f"Status: {display_status}")

def restore_game_button(game_process, game_name):
    """Restore a game button after its process closes."""
    game_process.wait()
    if game_name in game_buttons:
        game_buttons[game_name]["button"].config(text=f"Launch {game_name}", command=lambda: run_game(game_name))

def run_game(game_name):
    """Run a game as a separate process."""
    global game_instance
    
    if not ws_connection:
        print("Not connected to server")
        return
    
    if game_name not in games_data:
        print(f"Game {game_name} not found")
        return
    
    game_port = games_data[game_name].get("port")
    game_path = games_data[game_name].get("path")
    
    if not game_path:
        print(f"Game path not found for {game_name}")
        return
    
    try:
        window.update()
    
        client_dir = Path(__file__).parent
        game_dir = client_dir.parent / "games" / game_path / "game"
        game_path_file = game_dir / "main.py"
        
        print(f"Launching {game_name} from {game_dir}")
        
        game_instance = subprocess.Popen(
            [sys.executable, str(game_path_file), player_name, "--port", str(game_port)], 
            cwd=str(game_dir)
        )

        if game_name in game_buttons:
            game_buttons[game_name]["button"].config(text="Close Game", command=lambda: close_game(game_name))

        watch_thread = threading.Thread(target=restore_game_button, args=(game_instance, game_name), daemon=True)
        watch_thread.start()
        
    except Exception as e:
        print(f"Error launching game: {str(e)}")

def close_game(game_name):
    """Close the currently running game process."""
    global game_instance

    if game_instance:
        game_instance.terminate()
        game_instance = None
        if game_name in game_buttons:
            game_buttons[game_name]["button"].config(text=f"Launch {game_name}", command=lambda: run_game(game_name))

# create main window
window = tk.Tk()
window.title(f"Resonance - {player_name}")
window.geometry("700x600")

# server connection status display
connection_label = tk.Label(window, text="Disconnected from Server", font=("Arial", 10))
connection_label.pack(pady=5)

# player name display
player_label = tk.Label(window, text=f"Player: {player_name}", font=("Arial", 9))
player_label.pack(pady=2)

# create a centered frame for games
center_frame = tk.Frame(window)
center_frame.pack(fill=tk.BOTH, expand=True)

games_frame = tk.Frame(center_frame)
games_frame.pack(expand=True, anchor="center")

def main():
    """Main function to start the client."""

    # start the persistent connection
    threading.Thread(target=lambda: asyncio.run(persistent_connection()), daemon=True).start()

    # allow the window close button to stop the app
    window.protocol("WM_DELETE_WINDOW", lambda: (game_instance.terminate() if game_instance else None, window.destroy()))

    # show the window
    try:
        window.mainloop()
    except KeyboardInterrupt:
        if game_instance:
            game_instance.terminate()
        if window.winfo_exists():
            window.destroy()
        print("\nClient stopped.")

# entry point to start the client
if __name__ == "__main__":
    main()

