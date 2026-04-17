# used for the UI
import tkinter as tk

# needed to open the game as a separate process and watch for it to close
import subprocess

import sys
import os

# used for the async server checks
import asyncio

# used to connect to the Python server
import websockets

# used for background threads to keep the UI running while checking server status and watching the game process
import threading

# track servers and game status
py_running = False
cpp_running = False
game_instance = None

async def check_py():
    """Check if the Python server is running"""
    try:
        async with websockets.connect("ws://127.0.0.1:8000") as ws:
            return True
    except Exception as e:
        return False

async def check_cpp():
    """Check if the C++ server is running"""
    try:
        async with websockets.connect("ws://127.0.0.1:8000") as ws:
            await ws.send("check_cpp")
            result = await ws.recv()
            return result == "ready"
    except Exception as e:
        return False

def check_status():
    """Check if both servers are running and schedule next check"""
    global py_running, cpp_running
    try:
        py_running = asyncio.run(check_py())
        
        if py_running:
            cpp_running = asyncio.run(check_cpp())
        else:
            cpp_running = False
        
        display_status()
    except Exception as e:
        print(f"Connection check failed: {e}")
        py_running = False
        cpp_running = False
        display_status()
    
    # schedule next check in 1 second
    window.after(1000, check_status)

def display_status():
    """Update the status labels in the UI"""
    if py_running:
        py_label.config(text="Python Server: Connected", fg="green")
    else:
        py_label.config(text="Python Server: Not Connected", fg="red")
    
    if cpp_running:
        cpp_label.config(text="C++ Server: Connected", fg="green")
    else:
        cpp_label.config(text="C++ Server: Not Connected", fg="red")

def game_status(proc):
    """Wait for the game to close and update the game button"""
    proc.wait()
    game_button.config(text="Launch Game", command=open_game)

def open_game():
    """Open the game if both servers are running"""
    global game_instance
    
    if not py_running or not cpp_running:
        py_label.config(text="Python Server: Not Connected", fg="red")
        cpp_label.config(text="C++ Server: Not Connected", fg="red")
        return
    
    try:
        window.update()
    
        # build path to the game
        game_path = os.path.join(os.path.dirname(__file__), "game_client", "game", "main.py")
        game_dir = os.path.dirname(game_path)
        
        # start the game as a separate process
        game_instance = subprocess.Popen([sys.executable, game_path, "Player1"], cwd=game_dir)
        
        # update the game button
        game_button.config(text="Close Game", command=close_game)
        
        # start a thread to watch for the game to close
        watch_thread = threading.Thread(target=game_status, args=(game_instance,), daemon=True)
        watch_thread.start()
        
    except Exception as e:
        py_label.config(text=f"Error: {str(e)}", fg="red")

def close_game():
    """Close the game"""
    global game_instance
    if game_instance:
        game_instance.terminate()
        game_instance = None

# create main window
window = tk.Tk()
window.title("Resonance")
window.geometry("300x150")

# server status display
py_label = tk.Label(window, text="Python Server: Checking...", font=("Arial", 10), fg="orange")
py_label.pack(pady=5)

cpp_label = tk.Label(window, text="C++ Server: Checking...", font=("Arial", 10), fg="orange")
cpp_label.pack(pady=5)

# launch game button
game_button = tk.Button(window, text="Launch Game", command=open_game, font=("Arial", 12), width=15)
game_button.pack(pady=10)

# start the status check loop
check_status()

# show the window
window.mainloop()
