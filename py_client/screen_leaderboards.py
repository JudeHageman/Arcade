# used for the UI
import tkinter as tk

class LeaderboardsScreen:
    """Leaderboards screen and query controls."""

    def __init__(self, parent, send_query):
        """Build leaderboard controls and output text area."""
        # top controls used to request leaderboard rows
        self.send_query = send_query
        self.widget = tk.Frame(parent)

        lb_controls = tk.Frame(self.widget)
        lb_controls.pack(pady=2)
        tk.Label(lb_controls, text="Game:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.lb_game_entry = tk.Entry(lb_controls, font=("Arial", 9), width=16)
        self.lb_game_entry.insert(0, "Immortal Tree")
        self.lb_game_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(lb_controls, text="Mode:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.lb_mode_var = tk.StringVar(value="best_score")
        for _val, _label in [
            ("best_score", "Best Score"),
            ("total_score", "Total Score"),
            ("play_time", "Play Time"),
            ("team_score", "Team Score"),
        ]:
            tk.Radiobutton(lb_controls, text=_label, variable=self.lb_mode_var, value=_val, font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(lb_controls, text="Load", font=("Arial", 9), command=self.load).pack(side=tk.LEFT, padx=6)

        self.lb_text = tk.Text(self.widget, height=10, width=40, state=tk.DISABLED, font=("Arial", 9))
        self.lb_text.pack(padx=10, pady=6)

    def load(self):
        """Request leaderboard rows for current control values."""
        self.send_query({
            "action": "query",
            "query": "leaderboard",
            "game": self.lb_game_entry.get().strip(),
            "sort_by": self.lb_mode_var.get(),
            "top_n": 20
        })

    def display_leaderboard(self, data):
        """Render leaderboard response rows."""
        # overwrite current leaderboard content
        self.lb_text.config(state=tk.NORMAL)
        self.lb_text.delete(1.0, tk.END)
        rows = data.get("rows", [])
        own_rank = data.get("own_rank")
        sort_by = data.get("sort_by", self.lb_mode_var.get())
        if sort_by == "team_score":
            if own_rank is not None:
                self.lb_text.insert(tk.END, f"Your team rank: #{own_rank}\n\n")
            else:
                self.lb_text.insert(tk.END, "Your team rank: not ranked\n\n")
            if rows:
                for i, row in enumerate(rows, 1):
                    self.lb_text.insert(tk.END, f"{i}: {row.get('team','')} | {row.get('score',0)}\n")
            else:
                self.lb_text.insert(tk.END, "No data.\n")
        else:
            if own_rank is not None:
                self.lb_text.insert(tk.END, f"Your rank: #{own_rank}\n\n")
            else:
                self.lb_text.insert(tk.END, "Your rank: not ranked\n\n")
            if rows:
                for i, row in enumerate(rows, 1):
                    self.lb_text.insert(tk.END, f"{i}: {row.get('username','')} | {row.get('score',0)}\n")
            else:
                self.lb_text.insert(tk.END, "No data.\n")
        self.lb_text.config(state=tk.DISABLED)


def build_leaderboards_screen(parent, send_query):
    """Create and return leaderboards widget plus display callback."""
    screen = LeaderboardsScreen(parent, send_query)
    return screen.widget, screen.display_leaderboard
