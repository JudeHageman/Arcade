import tkinter as tk
import subprocess
import sys
import os
import urllib.request
import threading

connected = False
game_process = None

def connect():
    """Connect to Python server and check if C++ server is available"""
    global connected
    try:
        response = urllib.request.urlopen('http://127.0.0.1:8000/launch')
        status = response.read().decode('utf-8')
        
        if status == 'ready':
            status_label.config(text="Connected!", fg="green")
            connected = True
        else:
            status_label.config(text="C++ Server Error", fg="red")
            connected = False
    except Exception as e:
        status_label.config(text="Server Error", fg="red")
        connected = False

def monitor(process):
    """Monitor when game closes and update status"""
    process.wait()
    status_label.config(text="Game Disconnected", fg="red")

def launch():
    """Launch game if connected"""
    global game_process
    
    if not connected:
        status_label.config(text="Not Connected", fg="red")
        return
    
    try:
        status_label.config(text="Game Launching...", fg="blue")
        window.update()
        
        # Open the game client
        game_client = os.path.join(os.path.dirname(__file__), "lab-05", "code", "game", "main.py")
        game_folder = os.path.dirname(game_client)
        game_process = subprocess.Popen([sys.executable, game_client, "Player1"], cwd=game_folder)
        
        status_label.config(text="Game Running...", fg="green")
        
        # Monitor game in background
        monitor_thread = threading.Thread(target=monitor, args=(game_process,), daemon=True)
        monitor_thread.start()
        
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")

window = tk.Tk()
window.title("Resonance")
window.geometry("250x150")

connect_button = tk.Button(window, text="Connect", command=connect, font=("Arial", 12), width=15)
connect_button.pack(pady=10)

launch_button = tk.Button(window, text="Launch Game", command=launch, font=("Arial", 12), width=15)
launch_button.pack(pady=10)

status_label = tk.Label(window, text="Not Connected", font=("Arial", 11), fg="red")
status_label.pack(pady=10)

window.mainloop()
