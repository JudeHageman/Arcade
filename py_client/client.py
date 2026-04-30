# used for the UI
import tkinter as tk

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
team_widget = None

def change_screen(screen_name):
    """Switch between different screens."""
    global current_screen
    current_screen = screen_name
    
    # hide all screens
    for w in (games_widget, profile_widget, leaderboards_widget,
              player_search_widget, match_history_widget, games_catalog_widget):
        if w:
            w.pack_forget()
    
    # show the selected screen
    if screen_name == "games" and games_widget:
        games_widget.pack(fill=tk.BOTH, expand=True)
    elif screen_name == "profile" and profile_widget:
        profile_widget.pack(fill=tk.BOTH, expand=True)
        send_query({"action": "query", "query": "profile"})
    elif screen_name == "leaderboards" and leaderboards_widget:
        leaderboards_widget.pack(fill=tk.BOTH, expand=True)
    elif screen_name == "player_search" and player_search_widget:
        player_search_widget.pack(fill=tk.BOTH, expand=True)
    elif screen_name == "match_history" and match_history_widget:
        match_history_widget.pack(fill=tk.BOTH, expand=True)
    elif screen_name == "games_catalog" and games_catalog_widget:
        games_catalog_widget.pack(fill=tk.BOTH, expand=True)

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
            main_widget.pack(fill=tk.BOTH, expand=True)
        change_screen("games")

def clear_game_state():
    """Clear all game and chat state from the client UI and memory."""
    global games_data, loaded_games

    games_data = HashTable()
    loaded_games = HashTable()
    game_buttons.clear()
    chat_widgets.clear()

    for widget in games_widget.winfo_children():
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
    player_label.config(text=f"Player: {player_name}")
    team_label.config(text=f"Team: {team.capitalize()}")
    window.title(f"Resonance - {player_name}")

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

    def retry_connection():
        try:
            asyncio.run(persistent_connection())
        except Exception:
            pass

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
            for widget in games_widget.winfo_children():
                widget.destroy()
            game_buttons.clear()
            chat_widgets.clear()
            label = tk.Label(games_widget, text="No games available", font=("Arial", 10))
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
        for widget in games_widget.winfo_children():
            widget.destroy()
        game_buttons.clear()
        chat_widgets.clear()

        # create UI for each game
        for i in range(games_data.capacity):
            for game_name, game_info in games_data.table[i]:
                create_game_ui(game_name, game_info)

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
    game_container = tk.Frame(games_widget, relief=tk.SUNKEN, bd=1, width=400)
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
    global game_instance
    game_process.wait()
    # Only restore the button if the game_instance hasn't been manually set to None (by user closing)
    if game_instance is not None and game_instance.pid == game_process.pid:
        if game_name in game_buttons:
            game_buttons.get(game_name)["button"].config(text=f"Launch {game_name}", command=lambda: run_game(game_name))

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
            game_buttons.get(game_name)["button"].config(text=f"Launch {game_name}", command=lambda: run_game(game_name))

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

# login
login_widget = tk.Frame(window)

tk.Label(login_widget, text="Username", font=("Arial", 9)).grid(row=0, column=0, padx=5, pady=2, sticky="e")
username_entry = tk.Entry(login_widget, font=("Arial", 9), width=20)
username_entry.grid(row=0, column=1, padx=5, pady=2)

tk.Label(login_widget, text="Password", font=("Arial", 9)).grid(row=1, column=0, padx=5, pady=2, sticky="e")
password_entry = tk.Entry(login_widget, font=("Arial", 9), width=20, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=2)

login_button = tk.Button(login_widget, text="Login", font=("Arial", 9), command=send_login)
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
team_widget = tk.Frame(window)
tk.Label(team_widget, text="Choose your team:", font=("Arial", 9)).pack(pady=(4, 2))
team_btn_frame = tk.Frame(team_widget)
team_btn_frame.pack()
for _team, _color in [("pink", "#ffb6c1"), ("green", "#b4eeb4"), ("blue", "#add8e6")]:
    tk.Button(
        team_btn_frame,
        text=_team.capitalize(),
        font=("Arial", 9),
        width=10,
        command=lambda t=_team: send_team(t)
    ).pack(side=tk.LEFT, padx=6)

# navigation frame with buttons for different screens (placed in header)
navigation_frame = tk.Frame(window)
button_frame = tk.Frame(navigation_frame)
button_frame.pack(expand=True)
tk.Button(button_frame, text="Games", font=("Arial", 9), command=lambda: change_screen("games")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Game Catalog", font=("Arial", 9), command=lambda: change_screen("games_catalog")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Leaderboards", font=("Arial", 9), command=lambda: change_screen("leaderboards")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Player Search", font=("Arial", 9), command=lambda: change_screen("player_search")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Match History", font=("Arial", 9), command=lambda: change_screen("match_history")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Profile", font=("Arial", 9), command=lambda: change_screen("profile")).pack(side=tk.LEFT, padx=3)
tk.Button(button_frame, text="Logout", font=("Arial", 9), command=logout).pack(side=tk.LEFT, padx=3)

# create a centered frame for main content
main_widget = tk.Frame(window)

# content frame to hold all screens
content_frame = tk.Frame(main_widget)
content_frame.pack(fill=tk.BOTH, expand=True)

# games screen
games_widget = tk.Frame(content_frame)

# profile screen
profile_widget = tk.Frame(content_frame)
profile_text = tk.Text(profile_widget, height=10, width=40, state=tk.DISABLED, font=("Arial", 9))
profile_text.pack(padx=10, pady=6)

def display_profile(data):
    """Render a profile dict into the profile text box."""
    profile_text.config(state=tk.NORMAL)
    profile_text.delete(1.0, tk.END)
    if not data:
        profile_text.insert(tk.END, "No profile found.\n")
    else:
        profile_text.insert(tk.END, f"Username: {data.get('username', 'N/A')}\n")
        profile_text.insert(tk.END, f"Team: {data.get('team', 'N/A')}\n")
        profile_text.insert(tk.END, f"Total Games: {data.get('total_games', 0)}\n")
        profile_text.insert(tk.END, f"Total Score: {data.get('total_score', 0)}\n")
        profile_text.insert(tk.END, f"Best Score: {data.get('best_score', 0)}\n")
        profile_text.insert(tk.END, f"Total Time: {data.get('total_time', 0)}s\n")
        history = data.get("score_history", [])
        if history:
            profile_text.insert(tk.END, "\nRecent Scores:\n")
            for entry in history[:10]:
                profile_text.insert(tk.END, f"{entry.get('timestamp','')[:19]} {entry.get('game','')} {entry.get('score',0)}\n")
    profile_text.config(state=tk.DISABLED)


# leaderboards screen
leaderboards_widget = tk.Frame(content_frame)

lb_controls = tk.Frame(leaderboards_widget)
lb_controls.pack(pady=2)
tk.Label(lb_controls, text="Game:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
lb_game_entry = tk.Entry(lb_controls, font=("Arial", 9), width=16)
lb_game_entry.insert(0, "Immortal Tree")
lb_game_entry.pack(side=tk.LEFT, padx=2)
tk.Label(lb_controls, text="Mode:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
lb_mode_var = tk.StringVar(value="best_score")
for _val, _label in [("best_score", "Best Score"), ("total_score", "Total Score"), ("play_time", "Play Time")]:
    tk.Radiobutton(lb_controls, text=_label, variable=lb_mode_var, value=_val, font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
tk.Button(lb_controls, text="Load", font=("Arial", 9),
    command=lambda: send_query({"action": "query", "query": "leaderboard",
        "game": lb_game_entry.get().strip(), "sort_by": lb_mode_var.get(), "top_n": 20})).pack(side=tk.LEFT, padx=6)

lb_text = tk.Text(leaderboards_widget, height=10, width=40, state=tk.DISABLED, font=("Arial", 9))
lb_text.pack(padx=10, pady=6)

def display_leaderboard(data):
    """Render leaderboard response into the leaderboard text box."""
    lb_text.config(state=tk.NORMAL)
    lb_text.delete(1.0, tk.END)
    rows = data.get("rows", [])
    own_rank = data.get("own_rank")
    if own_rank:
        lb_text.insert(tk.END, f"Your rank: #{own_rank}\n")
    lb_text.insert(tk.END, "\n")
    if not rows:
        lb_text.insert(tk.END, "No data.\n")
    else:
        for i, row in enumerate(rows, 1):
            lb_text.insert(tk.END, f"{i} {row.get('username','')} {row.get('score',0)}\n")
    lb_text.config(state=tk.DISABLED)


# player search screen
player_search_widget = tk.Frame(content_frame)

ps_controls = tk.Frame(player_search_widget)
ps_controls.pack(pady=2)
tk.Label(ps_controls, text="Prefix:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
ps_entry = tk.Entry(ps_controls, font=("Arial", 9), width=20)
ps_entry.pack(side=tk.LEFT, padx=2)
tk.Button(ps_controls, text="Search", font=("Arial", 9),
    command=lambda: send_query({"action": "query", "query": "player_search",
        "prefix": ps_entry.get().strip()})).pack(side=tk.LEFT, padx=6)

ps_list = tk.Listbox(player_search_widget, font=("Arial", 9), height=10, width=40)
ps_list.pack(padx=10, pady=4)

ps_detail_text = tk.Text(player_search_widget, height=10, width=40, state=tk.DISABLED, font=("Arial", 9))
ps_detail_text.pack(padx=10, pady=4)

_ps_results = []

def display_search_results(results):
    """Populate the player search listbox with results."""
    global _ps_results
    _ps_results = results or []
    ps_list.delete(0, tk.END)
    for r in _ps_results:
        ps_list.insert(tk.END, f"{r.get('username','')}  ({r.get('team','')})")

def _on_ps_select(event):
    """Load full profile for the selected player."""
    sel = ps_list.curselection()
    if not sel or not _ps_results:
        return
    idx = sel[0]
    if idx < len(_ps_results):
        username = _ps_results[idx].get("username", "")
        send_query({"action": "query", "query": "player_profile", "username": username})

ps_list.bind("<<ListboxSelect>>", _on_ps_select)

def display_player_profile(data):
    """Render a player profile in the player search detail area."""
    ps_detail_text.config(state=tk.NORMAL)
    ps_detail_text.delete(1.0, tk.END)
    if not data:
        ps_detail_text.insert(tk.END, "Player not found.\n")
    else:
        ps_detail_text.insert(tk.END, f"Username: {data.get('username','')}\n")
        ps_detail_text.insert(tk.END, f"Team: {data.get('team','N/A')}\n")
        ps_detail_text.insert(tk.END, f"Total Games: {data.get('total_games',0)}\n")
        ps_detail_text.insert(tk.END, f"Total Score: {data.get('total_score',0)}\n")
        ps_detail_text.insert(tk.END, f"Best Score: {data.get('best_score',0)}\n")
    ps_detail_text.config(state=tk.DISABLED)


# match history screen
match_history_widget = tk.Frame(content_frame)

mh_controls = tk.Frame(match_history_widget)
mh_controls.pack(pady=2)
tk.Label(mh_controls, text="Username:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
mh_user_entry = tk.Entry(mh_controls, font=("Arial", 9), width=16)
mh_user_entry.pack(side=tk.LEFT, padx=2)
tk.Label(mh_controls, text="Game (opt):", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
mh_game_entry = tk.Entry(mh_controls, font=("Arial", 9), width=14)
mh_game_entry.pack(side=tk.LEFT, padx=2)

def _send_match_history():
    """Read the match history filter fields and send the query to the server."""
    username = mh_user_entry.get().strip() or player_name
    game_filter = mh_game_entry.get().strip() or None
    send_query({"action": "query", "query": "match_history",
        "username": username, "game": game_filter})

tk.Button(mh_controls, text="Load", font=("Arial", 9), command=_send_match_history).pack(side=tk.LEFT, padx=6)

mh_text = tk.Text(match_history_widget, height=10, width=40, state=tk.DISABLED, font=("Arial", 9))
mh_text.pack(padx=10, pady=6)

def display_match_history(data):
    """Render match history rows into the match history text box."""
    mh_text.config(state=tk.NORMAL)
    mh_text.delete(1.0, tk.END)
    if not data:
        mh_text.insert(tk.END, "No matches found.\n")
    else:
        for row in data:
            mh_text.insert(tk.END,
                f"{row.get('timestamp','')[:19]} {row.get('game','')} {row.get('individual_score',0)} {row.get('team_score',0)} {row.get('game_time',0)}s\n")
    mh_text.config(state=tk.DISABLED)


# games catalog screen
games_catalog_widget = tk.Frame(content_frame)

gc_controls = tk.Frame(games_catalog_widget)
gc_controls.pack(pady=2)
tk.Label(gc_controls, text="Sort by:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
gc_sort_var = tk.StringVar(value="most_played")
for _val, _label in [("most_played", "Most Played"), ("highest_avg_score", "Highest Avg Score"), ("most_recently_active", "Most Recently Active")]:
    tk.Radiobutton(gc_controls, text=_label, variable=gc_sort_var, value=_val, font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
tk.Button(gc_controls, text="Load", font=("Arial", 9),
    command=lambda: send_query({"action": "query", "query": "games_catalog",
        "sort_by": gc_sort_var.get()})).pack(side=tk.LEFT, padx=6)

gc_text = tk.Text(games_catalog_widget, height=10, width=40, state=tk.DISABLED, font=("Arial", 9))
gc_text.pack(padx=10, pady=6)

def display_games_catalog(rows):
    """Render games catalog rows into the catalog text box."""
    gc_text.config(state=tk.NORMAL)
    gc_text.delete(1.0, tk.END)
    if not rows:
        gc_text.insert(tk.END, "No games found.\n")
    else:
        for row in rows:
            gc_text.insert(tk.END,
                f"{row.get('name','')} {row.get('total_sessions',0)} {row.get('avg_score',0.0)} {row.get('last_played','')[:19]}\n")
    gc_text.config(state=tk.DISABLED)


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

