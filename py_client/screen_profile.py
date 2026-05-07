# used for the UI
import tkinter as tk

class ProfileScreen:
    """Profile screen container and renderer."""

    def __init__(self, parent, get_player_name):
        """Build profile widgets."""
        # profile screen text viewer
        self.get_player_name = get_player_name
        self.widget = tk.Frame(parent)
        self.profile_text = tk.Text(self.widget, height=10, width=40, state=tk.DISABLED, font=("Arial", 9))
        self.profile_text.pack(padx=10, pady=6)

    def display_profile(self, data):
        """Render a profile payload into the profile text box."""
        render_profile_text(self.profile_text, data, fallback_username=self.get_player_name())

def format_session_row(row):
    """Format a single match-history row."""
    # format one match history line
    game_name = row.get("game", "")
    timestamp = row.get("timestamp", "")[:19]
    individual_score = row.get("individual_score", row.get("score", 0))
    team_score = row.get("team_score", 0)
    game_time = row.get("game_time", 0)
    return f"{game_name}: {timestamp} | {individual_score} | {team_score} | {game_time}s"

def render_profile_text(target_text_widget, data, fallback_username=None):
    """Render shared profile fields in a target text widget."""
    # clear old text before rendering profile details
    target_text_widget.config(state=tk.NORMAL)
    target_text_widget.delete(1.0, tk.END)
    if not data:
        target_text_widget.insert(tk.END, "No profile found.\n")
    else:
        username = data.get("username", None) or fallback_username or ""
        target_text_widget.insert(tk.END, f"Username: {username}\n")
        target_text_widget.insert(tk.END, f"Team: {data.get('team', 'N/A')}\n")
        target_text_widget.insert(tk.END, f"Total Games: {data.get('total_games', 0)}\n")
        target_text_widget.insert(tk.END, f"Total Score: {data.get('total_score', 0)}\n")
        target_text_widget.insert(tk.END, f"Total Team Score: {data.get('total_team_score', 0)}\n")
        target_text_widget.insert(tk.END, f"Best Score: {data.get('best_score', 0)}\n")
        target_text_widget.insert(tk.END, f"Total Time: {data.get('total_time', 0)}s\n")
    target_text_widget.config(state=tk.DISABLED)

def build_profile_screen(parent, get_player_name):
    """Create and return profile widget plus display callback."""
    screen = ProfileScreen(parent, get_player_name)
    return screen.widget, screen.display_profile
