# used for the UI
import tkinter as tk

class GamesCatalogScreen:
    """Games catalog screen and sort controls."""

    def __init__(self, parent, send_query):
        """Build catalog controls and text area."""
        # sort controls for game catalog requests
        self.send_query = send_query
        self.widget = tk.Frame(parent)

        gc_controls = tk.Frame(self.widget)
        gc_controls.pack(pady=2)
        tk.Label(gc_controls, text="Sort by:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.gc_sort_var = tk.StringVar(value="most_played")
        for _val, _label in [
            ("most_played", "Most Played"),
            ("highest_avg_score", "Highest Avg Score"),
            ("team_score", "Team Score"),
            ("most_recently_active", "Most Recently Active"),
        ]:
            tk.Radiobutton(gc_controls, text=_label, variable=self.gc_sort_var, value=_val, font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(gc_controls, text="Load", font=("Arial", 9), command=self.load).pack(side=tk.LEFT, padx=6)

        self.gc_text = tk.Text(self.widget, height=10, width=40, state=tk.DISABLED, font=("Arial", 9))
        self.gc_text.pack(padx=10, pady=6)

    def load(self):
        """Request catalog rows for the active sort option."""
        self.send_query({"action": "query", "query": "games_catalog", "sort_by": self.gc_sort_var.get()})

    def display_games_catalog(self, rows):
        """Render game rows using the active sort metric."""
        # show only the metric tied to active sort mode
        self.gc_text.config(state=tk.NORMAL)
        self.gc_text.delete(1.0, tk.END)
        if not rows:
            self.gc_text.insert(tk.END, "No games found.\n")
        else:
            sort_mode = self.gc_sort_var.get()
            for row in rows:
                game_name = row.get("name", "")
                if sort_mode == "highest_avg_score":
                    self.gc_text.insert(tk.END, f"{game_name}: {row.get('avg_score', 0.0)}\n")
                elif sort_mode == "team_score":
                    self.gc_text.insert(tk.END, f"{game_name}: {row.get('total_team_score', 0)}\n")
                elif sort_mode == "most_recently_active":
                    self.gc_text.insert(tk.END, f"{game_name}: {row.get('last_played', '')[:19]}\n")
                else:
                    self.gc_text.insert(tk.END, f"{game_name}: {row.get('total_sessions', 0)}\n")
        self.gc_text.config(state=tk.DISABLED)


def build_games_catalog_screen(parent, send_query):
    """Create and return catalog widget plus display callback."""
    screen = GamesCatalogScreen(parent, send_query)
    return screen.widget, screen.display_games_catalog
