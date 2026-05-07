# used for the UI
import tkinter as tk

class TeamChatScreen:
    """Team chat screen with history and input box."""

    def __init__(self, parent, send_team_chat_callback):
        """Build team chat widgets."""
        # team chat pane with input and send button
        self.send_team_chat_callback = send_team_chat_callback
        self.widget = tk.Frame(parent)

        self.team_chat_display = tk.Text(
            self.widget,
            height=18,
            width=50,
            state=tk.DISABLED,
            font=("Arial", 9),
            bg="#1a1a1a"
        )
        self.team_chat_display.pack(padx=10, pady=5)

        team_chat_input_frame = tk.Frame(self.widget)
        team_chat_input_frame.pack(pady=4, padx=10)

        self.team_chat_input = tk.Entry(team_chat_input_frame, font=("Arial", 9), width=44)
        self.team_chat_input.pack(side=tk.LEFT, padx=5)

        tk.Button(team_chat_input_frame, text="Send", font=("Arial", 9), command=self.on_send).pack(side=tk.LEFT, padx=5)
        self.team_chat_input.bind("<Return>", lambda e: self.on_send())

    def on_send(self):
        """Send team chat message from input when valid."""
        message = self.team_chat_input.get().strip()
        if not message:
            return
        # clear entry only after successful send enqueue
        if self.send_team_chat_callback(message):
            self.team_chat_input.delete(0, tk.END)

    def load_team_chat_history(self, messages):
        """Replace team chat view with history rows."""
        self.team_chat_display.config(state=tk.NORMAL)
        self.team_chat_display.delete(1.0, tk.END)
        for msg in messages:
            self.team_chat_display.insert(tk.END, f"{msg.get('sender','')}: {msg.get('message','')}\n")
        self.team_chat_display.see(tk.END)
        self.team_chat_display.config(state=tk.DISABLED)

    def append_team_chat_messages(self, messages):
        """Append new team chat rows to the existing display."""
        self.team_chat_display.config(state=tk.NORMAL)
        for msg in messages:
            self.team_chat_display.insert(tk.END, f"{msg.get('sender','')}: {msg.get('message','')}\n")
        self.team_chat_display.see(tk.END)
        self.team_chat_display.config(state=tk.DISABLED)


def build_team_chat_screen(parent, send_team_chat_callback):
    """Create and return team-chat widget plus update callbacks."""
    screen = TeamChatScreen(parent, send_team_chat_callback)
    return screen.widget, screen.load_team_chat_history, screen.append_team_chat_messages
