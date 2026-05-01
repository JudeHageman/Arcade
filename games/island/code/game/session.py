import json
import time

class Session:
    """Sends session information when the game session ends."""

    def __init__(self, player_name, game_name, get_scores_fn):
        self.player_name = player_name
        self.game_name = game_name
        self.get_scores_fn = get_scores_fn
        self.start_time = time.time()

    def print_session(self):
        """Prints final session information to stdout for the client to forward."""
        try:
            individual_score, team_score, team = self.get_scores_fn()
            game_time = int(time.time() - self.start_time)
            payload = json.dumps({
                "type": "user",
                "action": "score",
                "game": self.game_name,
                "individual_score": individual_score,
                "team": team,
                "team_score": team_score,
                "game_time": game_time
            })
            print(f"[USER] {payload}", flush=True)
        except Exception as e:
            print(f"[Debug] Session Error: {e}")  