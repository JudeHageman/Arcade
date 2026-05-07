# used for the UI
import tkinter as tk
import tkinter.ttk as ttk

# needed to open the game as a separate process and watch for it to close
import subprocess

# used for command line arguments to allow custom player name
import sys

# used to find the game paths relative to the client script
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "data_structures"))

# custom hash table for client state management
from hash_table import HashTable

# used for the async server checks
import asyncio

# used to connect to the Python server
import websockets

# used for background threads to keep the UI running while keeping the websocket open and watching the game process
import threading

# used for games library, chat history, and live chat messages
import json

# used to build the screens
from screen_games_catalog import build_games_catalog_screen
from screen_leaderboards import build_leaderboards_screen
from screen_match_history import build_match_history_screen
from screen_player_search import build_player_search_screen
from screen_profile import build_profile_screen
from screen_team_chat import build_team_chat_screen

# websocket connects to a URI, not just a port
server_port = 8000
server_url = f"ws://127.0.0.1:{server_port}"

# player name is assigned by the server after login
player_name = "N/A"
player_team = "default"

# client state
ws = None
ws_connection = False
ws_loop = None
authenticated = False
games_data = HashTable()
loaded_games = HashTable()
game_instance = None
running_game_name = None
game_buttons = HashTable()
username_entry = None
password_entry = None
chat_widgets = HashTable()
login_widget = None
main_widget = None
navigation_frame = None
games_widget = None
profile_widget = None
leaderboards_widget = None
player_search_widget = None
match_history_widget = None
games_catalog_widget = None
team_chat_widget = None
team_widget = None
player_search_on_show = None

def _retry_connection():
    """Try to re-establish the websocket connection in a new event loop."""
    try:
        asyncio.run(persistent_connection())
    except Exception:
        pass

def change_screen(screen_name):
    """Switch between different screens."""
    global current_screen
    current_screen = screen_name

    # hide all screens
    for w in (games_widget, profile_widget, leaderboards_widget,
              player_search_widget, match_history_widget, games_catalog_widget,
              team_chat_widget):
        if w:
            w.pack_forget()

    # show the selected screen
    if screen_name == "games" and games_widget:
        games_widget.pack(fill=tk.X)
    elif screen_name == "profile" and profile_widget:
        profile_widget.pack(fill=tk.X)
        send_query({"action": "query", "query": "profile"})
    elif screen_name == "leaderboards" and leaderboards_widget:
        leaderboards_widget.pack(fill=tk.X)
    elif screen_name == "player_search" and player_search_widget:
        player_search_widget.pack(fill=tk.X)
        if player_search_on_show:
            player_search_on_show()
    elif screen_name == "match_history" and match_history_widget:
        match_history_widget.pack(fill=tk.X)
    elif screen_name == "games_catalog" and games_catalog_widget:
        games_catalog_widget.pack(fill=tk.X)
    elif screen_name == "team_chat" and team_chat_widget:
        team_chat_widget.pack(fill=tk.X)

def change_view(view):
    """Switch the client between disconnected, login, and games views."""
    global player_name, authenticated

    if view == "disconnected":
        authenticated = False
        player_name = "N/A"
        if 'player_label' in globals():
            player_label.config(text="Player: N/A")
        if 'team_label' in globals():
            team_label.config(text="Team: N/A")
        if '_recolor' in globals():
            _recolor("white")
        if 'navigation_frame' in globals() and navigation_frame:
            navigation_frame.pack_forget()
        window.title("Resonance - N/A")
        if login_widget:
            login_widget.pack_forget()
        if main_widget:
            main_widget.pack_forget()
        if team_widget:
            team_widget.pack_forget()
        return

    if view == "login":
        if main_widget:
            main_widget.pack_forget()
        if 'navigation_frame' in globals() and navigation_frame:
            navigation_frame.pack_forget()
        if login_widget:
            login_widget.pack(pady=10)

        if username_entry:
            username_entry.config(state=tk.NORMAL)
        if password_entry:
            password_entry.config(state=tk.NORMAL)
            password_entry.delete(0, tk.END)
        if login_button:
            login_button.config(state=tk.NORMAL)
        return

    if view == "games":
        if login_widget:
            login_widget.pack_forget()
        if 'navigation_frame' in globals() and navigation_frame:
            navigation_frame.pack(fill=tk.X, padx=5, pady=5)
        if main_widget:
            main_widget.pack(fill=tk.X)
        change_screen("games")

def clear_game_state():
    """Clear all game and chat state from the client UI and memory."""
    global games_data, loaded_games

    games_data = HashTable()
    loaded_games = HashTable()
    game_buttons.clear()
    chat_widgets.clear()

    for widget in games_inner.winfo_children():
        widget.destroy()

def show_team_select():
    """Show the team selection buttons for new accounts."""
    if login_widget:
        login_widget.pack_forget()
    if team_widget:
        team_widget.pack(pady=6)

def hide_team_select():
    """Hide the team selection buttons."""
    if team_widget:
        team_widget.pack_forget()

def send_team(team):
    """Send the chosen team to the server to complete account creation."""
    global ws, ws_loop
    if not ws or not ws_loop:
        return
    payload = json.dumps({
        "action": "select_team",
        "team": team
    })
    asyncio.run_coroutine_threadsafe(ws.send(payload), ws_loop)
    hide_team_select()

def change_username(username, team="default"):
    """Update the displayed username and team after a successful login."""
    global player_name, authenticated

    authenticated = True
    player_name = username
    _team_color = TEAM_COLORS.get(team.lower(), TEAM_COLORS["default"])
    player_label.config(text=f"Player: {player_name}", fg=_team_color)
    team_label.config(text=f"Team: {team.capitalize()}", fg=_team_color)
    window.title(f"Resonance - {player_name}")
    _recolor(_team_color)

    if username_entry:
        username_entry.config(state=tk.DISABLED)
    if password_entry:
        password_entry.delete(0, tk.END)
        password_entry.config(state=tk.DISABLED)
    if login_button:
        login_button.config(state=tk.DISABLED)
    change_view("games")

def logout():
    """Close the WebSocket connection to logout."""
    global ws, ws_loop
    if ws and ws_loop:
        asyncio.run_coroutine_threadsafe(ws.close(), ws_loop)

def send_login():
    """Send the username and password to the server for authentication."""
    global ws, ws_loop

    if not ws_connection or not ws or not ws_loop:
        return

    username = username_entry.get().strip() if username_entry else ""
    password = password_entry.get() if password_entry else ""

    if not username or not password:
        return
    payload = json.dumps({
        "action": "login",
        "username": username,
        "password": password
    })
    asyncio.run_coroutine_threadsafe(ws.send(payload), ws_loop)

async def persistent_connection():
    """Maintain a persistent connection to the server, automatically reconnecting if the connection is lost."""
    global ws_connection, ws, ws_loop, games_data, authenticated, player_team

    try:
        async with websockets.connect(server_url) as ws_conn:
            ws = ws_conn
            ws_loop = asyncio.get_running_loop()
            ws_connection = True
            authenticated = False
            window.after(0, update_connection_status)  
            window.after(0, lambda: change_view("login"))

            # listen for messages from the server
            async for payload in ws_conn:
                try:
                    data = json.loads(payload)

                    if data.get("type") == "select_team":
                        window.after(0, show_team_select)
                        continue

                    if data.get("type") == "initial":
                        authenticated = True
                        username = data.get("username", "")
                        player_team = data.get("team", "default")
                        chat_history = data.get("chat_history", {})
                        for game_name, messages in chat_history.items():
                            try:
                                entry = games_data.get(game_name)
                            except KeyError:
                                entry = {}
                                games_data.put(game_name, entry)
                            entry["chat_history"] = messages
                        team_chat_history = data.get("team_chat_history", [])
                        window.after(0, lambda msgs=team_chat_history: _load_team_chat_history(msgs))
                        window.after(0, lambda u=username, t=player_team: change_username(u, t))
                        continue

                    if data.get("type") == "global":
                        if not authenticated:
                            continue
                        for game_name, game_info in data.get("games", {}).items():
                            if game_name not in games_data:
                                games_data.put(game_name, {})
                            games_data.get(game_name).update(game_info)
                        for game_name, messages in data.get("recent_chats", {}).items():
                            try:
                                entry = games_data.get(game_name)
                            except KeyError:
                                entry = {}
                                games_data.put(game_name, entry)
                            if "chat_history" not in entry:
                                entry["chat_history"] = []
                            entry["chat_history"].extend(messages)
                        window.after(0, update_games_ui)
                        continue

                    if data.get("type") == "team_chat_update":
                        if not authenticated:
                            continue
                        msgs = data.get("messages", [])
                        window.after(0, lambda m=msgs: _append_team_chat_messages(m))
                        continue

                    if data.get("type") == "profile":
                        window.after(0, lambda d=data.get("data"): display_profile(d))
                        continue

                    if data.get("type") == "leaderboard":
                        window.after(0, lambda d=data: display_leaderboard(d))
                        continue

                    if data.get("type") == "match_history":
                        window.after(0, lambda d=data.get("data"): display_match_history(d))
                        continue

                    if data.get("type") == "player_search":
                        window.after(0, lambda d=data.get("results"): display_search_results(d))
                        continue

                    if data.get("type") == "player_profile":
                        window.after(0, lambda d=data.get("data"): display_player_profile(d))
                        continue

                    if data.get("type") == "games_catalog":
                        window.after(0, lambda d=data.get("rows"): display_games_catalog(d))
                        continue

                except json.JSONDecodeError:
                    pass

    except Exception:
        pass

    # runs on both normal close and error
    ws_connection = False
    ws = None
    ws_loop = None
    window.after(0, lambda: change_view("disconnected"))
    window.after(0, clear_game_state)
    window.after(0, update_connection_status)

    window.after(3000, lambda: threading.Thread(target=_retry_connection, daemon=True).start())

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

    chat_display = chat_widgets.get(game_name).get("display")
    if chat_display:
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"{sender}: {message}\n")
        chat_display.see(tk.END)
        chat_display.config(state=tk.DISABLED)

def display_chat_history(game_name, messages):
    """Display the chat history for a specific game in the chat display."""
    if game_name not in chat_widgets:
        return

    chat_display = chat_widgets.get(game_name).get("display")
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

    chat_input = chat_widgets.get(game_name).get("input")
    if not chat_input:
        return

    message = chat_input.get()
    if not message.strip() or not ws_connection or not ws or not ws_loop or not authenticated:
        return

    try:
        payload = json.dumps({
            "action": "chat",
            "game": game_name,
            "message": message.strip()
        })
        asyncio.run_coroutine_threadsafe(ws.send(payload), ws_loop)

        chat_input.delete(0, tk.END)
    except Exception:
        pass

def update_games_ui():
    """Update the games UI based on the current games data received from the server."""
    global loaded_games

    if not ws_connection or not authenticated:
        return

    if games_data.size == 0:
        if game_buttons.size > 0:
            for widget in games_inner.winfo_children():
                widget.destroy()
            game_buttons.clear()
            chat_widgets.clear()
            label = tk.Label(games_inner, text="No games available", font=("Arial", 10))
            label.pack(pady=20)
            loaded_games = HashTable()
        return

    same_games = (games_data.size == loaded_games.size)
    if same_games:
        for i in range(games_data.capacity):
            for name, _ in games_data.table[i]:
                if name not in loaded_games:
                    same_games = False
                    break
            if not same_games:
                break

    if not same_games:
        for widget in games_inner.winfo_children():
            widget.destroy()
        game_buttons.clear()
        chat_widgets.clear()

        # create UI for each game
        for i in range(games_data.capacity):
            for game_name, game_info in games_data.table[i]:
                create_game_ui(game_name, game_info)

        _recolor(TEAM_COLORS.get(player_team, "white"))

        loaded_games = HashTable()
        for i in range(games_data.capacity):
            for name, info in games_data.table[i]:
                loaded_games.put(name, info)
    else:
        # for games that are already loaded, just update their status and chat history
        for i in range(games_data.capacity):
            for game_name, game_info in games_data.table[i]:
                if game_name in game_buttons:
                    update_game_status(game_name, game_info)
                if game_name in chat_widgets:
                    display_chat_history(game_name, game_info.get("chat_history", []))

def create_game_ui(game_name, game_info):
    """Create the UI elements for a given game."""
    game_container = tk.Frame(games_inner, relief=tk.FLAT, bd=0, bg="black", width=400)
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

    game_buttons.put(game_name, {
        "button": button,
        "status_label": status_label
    })

    chat_display = tk.Text(
        game_container,
        height=10,
        width=40,
        state=tk.DISABLED,
        font=("Arial", 8),
        bg="#1a1a1a"
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

    chat_widgets.put(game_name, {
        "display": chat_display,
        "input": chat_input
    })

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
    button = game_buttons.get(game_name)["button"]

    # only update button text if game is not currently running
    if game_name != running_game_name:
        button.config(
            state=tk.NORMAL if status == "connected" else tk.DISABLED,
            text=f"Launch {game_name}"
        )
    else:
        button.config(state=tk.NORMAL)

    # update status label
    status_label = game_buttons.get(game_name)["status_label"]
    status_label.config(text=f"Status: {display_status}")

def _read_game_stdout(proc):
    """Read stdout from the game process, forwarding user messages via the existing WebSocket."""
    try:
        for line in proc.stdout:
            line = line.rstrip()
            if line.startswith("[USER] "):
                try:
                    user_data = json.loads(line[len("[USER] "):])
                    if ws and ws_loop and ws_connection and authenticated:
                        asyncio.run_coroutine_threadsafe(ws.send(json.dumps(user_data)), ws_loop)
                except Exception:
                    pass
    except Exception:
        pass

def _restore_game_button(game_process, game_name):
    """Restore a game button after its process closes."""
    global game_instance, running_game_name
    game_process.wait()
    # only restore the button if the game_instance hasn't been manually set to none (by user closing)
    if game_instance is not None and game_instance.pid == game_process.pid:
        running_game_name = None
        if game_name in game_buttons:
            try:
                info = games_data.get(game_name)
                status = info.get("status", "unknown") if info else "unknown"
            except Exception:
                status = "unknown"
            btn_state = tk.NORMAL if status == "connected" else tk.DISABLED
            game_buttons.get(game_name)["button"].config(
                text=f"Launch {game_name}",
                command=lambda: run_game(game_name),
                state=btn_state
            )

def run_game(game_name):
    """Run a game as a separate process."""
    global game_instance, running_game_name

    if not ws_connection or not authenticated:
        return

    if game_name not in games_data:
        return

    game_port = games_data.get(game_name).get("port")
    game_path = games_data.get(game_name).get("path")

    if not game_path:
        return

    try:
        window.update()

        client_dir = Path(__file__).parent
        game_dir = client_dir.parent / "games" / game_path / "game"
        game_path_file = game_dir / "main.py"

        # build command with --team [color] only if game supports resonance
        cmd = [sys.executable, str(game_path_file), player_name, "--port", str(game_port)]
        resonance = games_data.get(game_name).get("resonance", False)
        if resonance:
            cmd.extend(["--team", player_team])

        game_instance = subprocess.Popen(
            cmd,
            cwd=str(game_dir),
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        running_game_name = game_name

        threading.Thread(target=_read_game_stdout, args=(game_instance,), daemon=True).start()

        if game_name in game_buttons:
            game_buttons.get(game_name)["button"].config(text="Close Game", command=lambda: close_game(game_name))

        watch_thread = threading.Thread(target=_restore_game_button, args=(game_instance, game_name), daemon=True)
        watch_thread.start()

    except Exception:
        pass

def close_game(game_name):
    """Close the currently running game process."""
    global game_instance, running_game_name

    if game_instance:
        game_instance.terminate()
        game_instance = None
        running_game_name = None
        if game_name in game_buttons:
            try:
                info = games_data.get(game_name)
                status = info.get("status", "unknown") if info else "unknown"
            except Exception:
                status = "unknown"
            btn_state = tk.NORMAL if status == "connected" else tk.DISABLED
            game_buttons.get(game_name)["button"].config(
                text=f"Launch {game_name}",
                command=lambda: run_game(game_name),
                state=btn_state
            )

def send_query(payload):
    """Send a query request to the server."""
    global ws, ws_loop
    if not ws or not ws_loop or not ws_connection or not authenticated:
        return
    asyncio.run_coroutine_threadsafe(ws.send(json.dumps(payload)), ws_loop)

# create main window
window = tk.Tk()
window.title(f"Resonance - {player_name}")
window.geometry("700x600")
window.configure(bg="black")
window.option_add("*Frame.Background", "black")
window.option_add("*Label.Background", "black")
window.option_add("*Button.Background", "black")
window.option_add("*Entry.Background", "#1a1a1a")
window.option_add("*Text.Background", "#1a1a1a")
window.option_add("*Listbox.Background", "#1a1a1a")

TEAM_COLORS = {"pink": "#FFB6C1", "green": "#B4EEB4", "blue": "#ADD8E6", "default": "#555555"}

# decorative background canvas (drawn behind all other widgets)
_bg_canvas = tk.Canvas(window, highlightthickness=0)
_bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

def _draw_bg(*_):
    _bg_canvas.delete("all")
    w = max(window.winfo_width(), 1)
    h = max(window.winfo_height(), 1)
    _bg_canvas.configure(bg="black")
    _bg_canvas.create_oval(int(w*-0.1), int(h*-0.05), int(w*0.65), int(h*0.75), outline="#FFB6C1", width=2)
    _bg_canvas.create_oval(int(w*0.05), int(h*0.55), int(w*0.7), int(h*1.3), outline="#FFB6C1", width=1)
    _bg_canvas.create_oval(int(w*0.35), int(h*-0.2), int(w*1.1), int(h*0.7), outline="#B4EEB4", width=2)
    _bg_canvas.create_oval(int(w*0.1), int(h*0.4), int(w*0.95), int(h*1.3), outline="#B4EEB4", width=1)
    _bg_canvas.create_oval(int(w*-0.2), int(h*0.3), int(w*0.6), int(h*1.1), outline="#ADD8E6", width=2)
    _bg_canvas.create_oval(int(w*0.6), int(h*-0.1), int(w*1.05), int(h*0.45), outline="#ADD8E6", width=1)
    _bg_canvas.create_oval(int(w*0.55), int(h*0.2), int(w*1.15), int(h*0.9), outline="#FFB6C1", width=1)
    _bg_canvas.create_line(0, int(h*0.28), w, int(h*0.34), fill="#B4EEB4", width=1)
    _bg_canvas.create_line(0, int(h*0.72), w, int(h*0.66), fill="#ADD8E6", width=1)
    _bg_canvas.create_line(int(w*0.32), 0, int(w*0.38), h, fill="#FFB6C1", width=1)
    _bg_canvas.create_line(int(w*0.62), 0, int(w*0.58), h, fill="#B4EEB4", width=1)
    _bg_canvas.create_line(0, int(h*0.5), w, int(h*0.5), fill="#ADD8E6", width=1)

window.bind("<Configure>", _draw_bg)

def _recolor(fg):
    """Apply fg text color and black bg to all widgets."""
    _recolor_widget_tree(window, fg)

def _recolor_widget_tree(root_widget, fg):
    """Recursively apply the active theme colors to all descendants."""
    entry_bg = "#1a1a1a"
    stack = [root_widget]
    while stack:
        widget = stack.pop()
        cls = widget.winfo_class()
        try:
            if cls in ("Frame",):
                widget.configure(bg="black")
            elif cls == "Label":
                widget.configure(fg=fg, bg="black")
            elif cls == "Button":
                if widget in _team_btn_map:
                    widget.configure(fg=_team_btn_map[widget], activeforeground=_team_btn_map[widget], bg="black", activebackground="black")
                else:
                    widget.configure(fg=fg, bg="black", activeforeground=fg, activebackground="#222222")
            elif cls == "Entry":
                widget.configure(fg=fg, bg=entry_bg, insertbackground=fg)
            elif cls == "Text":
                widget.configure(fg=fg, bg=entry_bg)
            elif cls == "Listbox":
                widget.configure(fg=fg, bg=entry_bg)
            elif cls == "Radiobutton":
                widget.configure(fg=fg, bg="black", activebackground="black", selectcolor="black")
            elif cls == "Canvas":
                widget.configure(bg="black")
            elif cls == "Scrollbar":
                widget.configure(bg="#222222", troughcolor="black")
        except tk.TclError:
            pass
        stack.extend(widget.winfo_children())

# resonance title at the top centered
resonance_label = tk.Label(window, text="Resonance", font=("Arial", 22, "bold"), fg="white", bg="black")
resonance_label.pack(pady=(12, 2))

# login
login_widget = tk.Frame(window)

tk.Label(login_widget, text="Username", font=("Arial", 9)).grid(row=0, column=0, padx=5, pady=2, sticky="e")
username_entry = tk.Entry(login_widget, font=("Arial", 9), width=20)
username_entry.grid(row=0, column=1, padx=5, pady=2)

tk.Label(login_widget, text="Password", font=("Arial", 9)).grid(row=1, column=0, padx=5, pady=2, sticky="e")
password_entry = tk.Entry(login_widget, font=("Arial", 9), width=20, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=2)

login_button = tk.Button(login_widget, text="Create Account / Login", font=("Arial", 9), command=send_login)
login_button.grid(row=2, column=0, columnspan=2, pady=6)

# server connection status display
connection_label = tk.Label(window, text="Disconnected from Server", font=("Arial", 10))
connection_label.pack(pady=5)

# player name display
player_label = tk.Label(window, text="Player: N/A", font=("Arial", 9))
player_label.pack(pady=2)

team_label = tk.Label(window, text="Team: N/A", font=("Arial", 9))
team_label.pack(pady=0)

# team selection (shown only for new accounts, hidden by default)
_team_btn_map = {}  # maps button widget -> its team color, so _recolor preserves them
team_widget = tk.Frame(window)
tk.Label(team_widget, text="Choose your team:", font=("Arial", 9)).pack(pady=(4, 2))
team_btn_frame = tk.Frame(team_widget)
team_btn_frame.pack()
for _team, _color in [("pink", "#FFB6C1"), ("green", "#B4EEB4"), ("blue", "#ADD8E6")]:
    _tb = tk.Button(
        team_btn_frame,
        text=_team.capitalize(),
        font=("Arial", 10, "bold"),
        width=10,
        fg=_color,
        bg="black",
        activeforeground=_color,
        activebackground="black",
        relief=tk.RAISED,
        bd=2,
        command=lambda t=_team: send_team(t)
    )
    _tb.pack(side=tk.LEFT, padx=6)
    _team_btn_map[_tb] = _color

# navigation frame with buttons for different screens (placed in header)
navigation_frame = tk.Frame(window)
button_frame = tk.Frame(navigation_frame)
button_frame.pack(expand=True)
tk.Button(button_frame, text="Games", font=("Arial", 9), command=lambda: change_screen("games")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Game Catalog", font=("Arial", 9), command=lambda: change_screen("games_catalog")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Team Chat", font=("Arial", 9), command=lambda: change_screen("team_chat")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Leaderboards", font=("Arial", 9), command=lambda: change_screen("leaderboards")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Player Search", font=("Arial", 9), command=lambda: change_screen("player_search")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Match History", font=("Arial", 9), command=lambda: change_screen("match_history")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Profile", font=("Arial", 9), command=lambda: change_screen("profile")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Logout", font=("Arial", 9), command=logout).pack(side=tk.LEFT, padx=3)

# create a centered frame for main content
main_widget = tk.Frame(window)

# content frame to hold all screens
content_frame = tk.Frame(main_widget)
content_frame.pack(fill=tk.X)

# games screen
games_widget = tk.Frame(content_frame)
_games_canvas = tk.Canvas(games_widget, highlightthickness=0, bg="black", height=380)
_sb_style = ttk.Style()
_sb_style.theme_use("default")
_sb_style.configure("Dark.Vertical.TScrollbar", background="#2a2a2a", troughcolor="#111111", arrowcolor="#555555", bordercolor="#111111", darkcolor="#1a1a1a", lightcolor="#1a1a1a")
_games_scrollbar = ttk.Scrollbar(games_widget, orient="vertical", command=_games_canvas.yview, style="Dark.Vertical.TScrollbar")
games_inner = tk.Frame(_games_canvas)
_games_canvas.configure(yscrollcommand=_games_scrollbar.set)
_games_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
_games_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
_games_canvas_win = _games_canvas.create_window((0, 0), window=games_inner, anchor="nw")

def _on_games_inner_resize(event):
    _games_canvas.configure(scrollregion=_games_canvas.bbox("all"))

def _on_games_canvas_resize(event):
    _games_canvas.itemconfig(_games_canvas_win, width=event.width)

def _on_games_mousewheel(event):
    _games_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

games_inner.bind("<Configure>", _on_games_inner_resize)
_games_canvas.bind("<Configure>", _on_games_canvas_resize)
_games_canvas.bind("<MouseWheel>", _on_games_mousewheel)
games_inner.bind("<MouseWheel>", _on_games_mousewheel)

# profile/leaderboards/player-search/match-history/catalog/team-chat screens
profile_widget, display_profile = build_profile_screen(content_frame, lambda: player_name)
leaderboards_widget, display_leaderboard = build_leaderboards_screen(content_frame, send_query)
player_search_widget, display_search_results, display_player_profile, player_search_on_show = build_player_search_screen(content_frame, send_query)
match_history_widget, display_match_history = build_match_history_screen(content_frame, send_query)
games_catalog_widget, display_games_catalog = build_games_catalog_screen(content_frame, send_query)

def _send_team_chat_payload(message):
    """Send a team chat payload; return True on successful enqueue."""
    global ws, ws_loop
    if not message or not ws_connection or not ws or not ws_loop or not authenticated:
        return False
    try:
        asyncio.run_coroutine_threadsafe(
            ws.send(json.dumps({"action": "team_chat", "message": message})),
            ws_loop
        )
        return True
    except Exception:
        return False

team_chat_widget, _load_team_chat_history, _append_team_chat_messages = build_team_chat_screen(
    content_frame,
    _send_team_chat_payload
)

_draw_bg()
_recolor("white")

change_view("disconnected")

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

# entry point to start the client
if __name__ == "__main__":
    main()

