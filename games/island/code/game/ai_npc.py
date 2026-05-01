"""
ai_npc.py - Gemini AI integration for NPC dialog

Part 4 of Lab 7.

Setup (one-time)
----------------
1. Get a FREE API key at https://aistudio.google.com/
   (sign in with a Google account — no credit card required).

2. Install the SDK:
       pip install google-generativeai

3. Set your API key using ONE of these methods:

   Method A — environment variable (recommended; keeps key out of code):
       macOS / Linux:
           export GEMINI_API_KEY="your-key-here"
       Windows CMD:
           set GEMINI_API_KEY=your-key-here

   Method B — .env file (gitignored by default):
       Create a file named  .env  in the repo root:
           GEMINI_API_KEY=your-key-here
       Then install python-dotenv:
           pip install python-dotenv

What you need to do for Part 4
-------------------------------
1. Follow the setup steps above.
2. In dialog_data.py, give at least one NPC an AIHandler with a
   custom personality string.
3. Set that NPC's matching dialog node type to "ai":
       dg.add_dialog_node("chat", "...", node_type="ai")
4. Pass the AIHandler to the NPC entry in NPC_DATA.
5. Verify it works in-game: the NPC should display "..." briefly then
   show the Gemini-generated response.
"""

import os


class AIHandler:
    """
    Wraps the Gemini API to generate in-character NPC responses.

    Example usage (in dialog_data.py)::

        from ai_npc import AIHandler

        sage_ai = AIHandler(
            personality=(
                "You are Elara, an ancient sage in a fantasy RPG. "
                "You speak in riddles and old-world prose. "
                "Keep answers under three sentences."
            )
        )

    Then in NPC_DATA::

        {
            "name":       "Elara the Sage",
            "grid_x":     25,
            "grid_y":     14,
            "sprite_name": "sage",
            "dialog":     _make_sage_dialog(),
            "ai_handler": sage_ai,
        }
    """

    MODEL ="gemini-3-flash"

    def __init__(self, personality=(
        "You are an NPC in a fantasy RPG game. "
        "Stay in character. Respond in 2-3 sentences."
    )):
        self.personality = personality
        self._model      = None     # lazy-initialized on first call

    # ------------------------------------------------------------------

    def _ensure_model(self):
        if self._model is not None:
            return

        api_key = os.environ.get("GEMINI_API_KEY", "")

        if not api_key:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                api_key = os.environ.get("GEMINI_API_KEY", "")
            except ImportError:
                pass

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set.\n"
                "See ai_npc.py for setup instructions."
            )

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(self.MODEL)
        except ImportError:
            raise RuntimeError(
                "google-generativeai is not installed.\n"
                "Run: pip install google-generativeai"
            )

    # ------------------------------------------------------------------

    def generate(self, npc_name, player_message="Hello"):
        """
        Generate an in-character response.

        Args:
            npc_name      : NPC's name (used to personalise the prompt).
            player_message: What the player said (optional context).

        Returns:
            str: Generated response text.
        """
        self._ensure_model()
        prompt = (
            f"{self.personality}\n\n"
            f"Your name is {npc_name}.\n"
            f"The player approaches and says: \"{player_message}\".\n"
            f"Respond in character."
        )
        response = self._model.generate_content(prompt)
        return response.text.strip()
