import threading
import json
import time


class ScoreStatus:
    """Prints individual and team scores to stdout every second for the client to forward."""

    def __init__(self, player_name, game_name, get_scores_fn):
        self.player_name = player_name
        self.game_name = game_name
        self.get_scores_fn = get_scores_fn
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def _run(self):
        while True:
            try:
                individual_score, team_score, team = self.get_scores_fn()
                payload = json.dumps({
                    "type": "score",
                    "game": self.game_name,
                    "player": self.player_name,
                    "individual_score": individual_score,
                    "team": team,
                    "team_score": team_score
                })
                print(f"[SCORE]{payload}", flush=True)
            except Exception:
                pass
            time.sleep(1)
