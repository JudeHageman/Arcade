# used for the UI
import tkinter as tk

# used to format player search results
from screen_profile import render_profile_text
from dynamic_array import ArrayList

class PlayerSearchScreen:
    """Player search screen with list and detail panes."""

    def __init__(self, parent, send_query):
        """Build player search controls and widgets."""
        # search controls and results list
        self.send_query = send_query
        self.ps_results = ArrayList()
        self.ps_has_searched = False
        self.widget = tk.Frame(parent)

        ps_controls = tk.Frame(self.widget)
        ps_controls.pack(pady=2)
        tk.Label(ps_controls, text="Prefix:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.ps_entry = tk.Entry(ps_controls, font=("Arial", 9), width=20)
        self.ps_entry.pack(side=tk.LEFT, padx=2)

        self.ps_list = tk.Listbox(self.widget, font=("Arial", 9), height=10, width=40)
        self.ps_list.pack(padx=10, pady=4)

        self.ps_detail_text = tk.Text(self.widget, height=10, width=40, state=tk.DISABLED, font=("Arial", 9))
        self.ps_detail_text.pack(padx=10, pady=4)

        tk.Button(ps_controls, text="Search", font=("Arial", 9), command=self.send_player_search).pack(side=tk.LEFT, padx=6)
        self.ps_entry.bind("<Return>", lambda e: self.send_player_search())
        self.ps_list.bind("<<ListboxSelect>>", self.on_select)

    def show_message(self, message):
        """Show a status message in both list and detail panes."""
        # keep list and detail pane in sync for status messages
        self.ps_list.delete(0, tk.END)
        self.ps_list.insert(tk.END, message)
        self.ps_detail_text.config(state=tk.NORMAL)
        self.ps_detail_text.delete(1.0, tk.END)
        self.ps_detail_text.insert(tk.END, f"{message}\n")
        self.ps_detail_text.config(state=tk.DISABLED)

    def send_player_search(self):
        """Submit player prefix search from current input."""
        self.ps_has_searched = True
        prefix = self.ps_entry.get().strip()

        if not prefix:
            self.ps_results = ArrayList()
            self.show_message("No results found.")
            return

        # clear previous detail before loading new results
        self.ps_list.delete(0, tk.END)
        self.ps_detail_text.config(state=tk.NORMAL)
        self.ps_detail_text.delete(1.0, tk.END)
        self.ps_detail_text.config(state=tk.DISABLED)
        self.send_query({"action": "query", "query": "player_search", "prefix": prefix})

    def _set_results(self, results):
        """Store incoming search rows in the screen's ArrayList state."""
        self.ps_results = ArrayList()
        if not results:
            return
        for row in results:
            self.ps_results.append(row)

    def display_search_results(self, results):
        """Render player search result rows."""
        if not self.ps_has_searched:
            return
        self._set_results(results)
        self.ps_list.delete(0, tk.END)
        if len(self.ps_results) == 0:
            self.show_message("No results found.")
            return
        for row in self.ps_results:
            self.ps_list.insert(tk.END, f"{row.get('username','')}  ({row.get('team','')})")

    def on_select(self, event):
        """Load selected player's profile."""
        sel = self.ps_list.curselection()
        if not sel or not self.ps_results:
            return
        idx = sel[0]
        if idx < len(self.ps_results):
            username = self.ps_results[idx].get("username", "")
            self.send_query({"action": "query", "query": "player_profile", "username": username})

    def display_player_profile(self, data):
        """Render selected player profile in detail pane."""
        render_profile_text(self.ps_detail_text, data)

    def on_show(self):
        """Reset panes when screen first opens before searching."""
        # keep player search blank until first explicit search
        if not self.ps_has_searched:
            self.ps_list.delete(0, tk.END)
            self.ps_detail_text.config(state=tk.NORMAL)
            self.ps_detail_text.delete(1.0, tk.END)
            self.ps_detail_text.config(state=tk.DISABLED)


def build_player_search_screen(parent, send_query):
    """Create and return player-search widget plus handlers."""
    screen = PlayerSearchScreen(parent, send_query)
    return screen.widget, screen.display_search_results, screen.display_player_profile, screen.on_show
