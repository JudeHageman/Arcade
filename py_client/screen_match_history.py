# used for the UI
import tkinter as tk

# used to format match history rows
from screen_profile import format_session_row

class MatchHistoryScreen:
    """Match history screen with search and results."""

    def __init__(self, parent, send_query):
        """Build match-history controls and results area."""
        # filters for username and optional game
        self.send_query = send_query
        self.widget = tk.Frame(parent)

        mh_controls = tk.Frame(self.widget)
        mh_controls.pack(pady=2)
        tk.Label(mh_controls, text="Username:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.mh_user_entry = tk.Entry(mh_controls, font=("Arial", 9), width=16)
        self.mh_user_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(mh_controls, text="Game (opt):", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.mh_game_entry = tk.Entry(mh_controls, font=("Arial", 9), width=14)
        self.mh_game_entry.pack(side=tk.LEFT, padx=2)

        self.mh_text = tk.Text(self.widget, height=10, width=40, state=tk.DISABLED, font=("Arial", 9))
        self.mh_text.pack(padx=10, pady=6)

        tk.Button(mh_controls, text="Load", font=("Arial", 9), command=self.send_match_history).pack(side=tk.LEFT, padx=6)

    def send_match_history(self):
        """Submit a match-history query from current controls."""
        username = self.mh_user_entry.get().strip()
        game_filter = self.mh_game_entry.get().strip() or None
        if not username:
            self.mh_text.config(state=tk.NORMAL)
            self.mh_text.delete(1.0, tk.END)
            self.mh_text.insert(tk.END, "No results found.\n")
            self.mh_text.config(state=tk.DISABLED)
            return
        self.send_query({"action": "query", "query": "match_history", "username": username, "game": game_filter})

    def display_match_history(self, data):
        """Render match-history rows in the text area."""
        # replace text view with latest query results
        self.mh_text.config(state=tk.NORMAL)
        self.mh_text.delete(1.0, tk.END)
        if not data:
            self.mh_text.insert(tk.END, "No matches found.\n")
        else:
            rows = sorted(data, key=lambda row: row.get("timestamp", ""), reverse=True)
            rows.sort(key=lambda row: row.get("game", "").lower())
            for row in rows:
                self.mh_text.insert(tk.END, f"{format_session_row(row)}\n")
        self.mh_text.config(state=tk.DISABLED)


def build_match_history_screen(parent, send_query):
    """Create and return match-history widget plus display callback."""
    screen = MatchHistoryScreen(parent, send_query)
    return screen.widget, screen.display_match_history
