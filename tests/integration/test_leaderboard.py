"""
Tests for leaderboard.py
Run with: pytest test_leaderboard.py -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "py_server"))

from leaderboards import LeaderboardEntry
import pytest
import types

# ---------------------------------------------------------------------------
# Helpers to build fake session dicts
# ---------------------------------------------------------------------------

def make_session(game, username, score=0, play_time=0):
    return {
        "game": game,
        "username": username,
        "individual_score": score,
        "game_time": play_time,
    }


# ---------------------------------------------------------------------------
# Fixture: reload leaderboard with a controlled session list
# ---------------------------------------------------------------------------

@pytest.fixture()
def load_leaderboard(monkeypatch):
    """
    Factory fixture.  Call it with a list of session dicts and get back
    the freshly-imported leaderboard module.

    Usage:
        lb = load_leaderboard([make_session(...), ...])
    """
    def _load(sessions):
        # Remove cached module so the module-level init code re-runs
        for key in list(sys.modules.keys()):
            if "leaderboard" in key:
                del sys.modules[key]

        # Patch memory.sessions before the import triggers module-level code
        fake_memory = types.ModuleType("memory")
        fake_memory.sessions = sessions
        fake_memory.new_sessions = lambda: []
        monkeypatch.setitem(sys.modules, "memory", fake_memory)

        lb = __import__("leaderboards")  # Import after patching memory
        return lb

    return _load


# ===========================================================================
# LeaderboardEntry
# ===========================================================================

class TestLeaderboardEntry:

    def _entry(self, score, username):
        # Import without triggering module-level init
        for key in list(sys.modules.keys()):
            if "leaderboard" in key:
                del sys.modules[key]
        fake_memory = types.ModuleType("memory")
        fake_memory.sessions = []
        fake_memory.new_sessions = lambda: []
        sys.modules["memory"] = fake_memory
        return LeaderboardEntry(score, username)

    def test_higher_score_is_less(self):
        """Higher score sorts first (lt returns True for higher score)."""
        a = self._entry(100, "alice")
        b = self._entry(50, "bob")
        assert a < b  # a has higher score → comes first in BST

    def test_equal_score_tie_broken_by_username(self):
        """Tie broken alphabetically by username."""
        a = self._entry(100, "alice")
        b = self._entry(100, "zara")
        assert a < b  # "alice" < "zara"

    def test_same_entry_not_less_than_itself(self):
        a = self._entry(100, "alice")
        b = self._entry(100, "alice")
        assert not (a < b)

    def test_lower_score_is_not_less(self):
        a = self._entry(10, "alice")
        b = self._entry(200, "bob")
        assert not (a < b)


# ===========================================================================
# get_leaderboard
# ===========================================================================

class TestGetLeaderboard:

    def test_returns_list(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 50)])
        result = lb.get_leaderboard("pong")
        assert isinstance(result, list)

    def test_empty_for_unknown_game(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 50)])
        assert lb.get_leaderboard("nonexistent_game") == []

    def test_single_player(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 42)])
        result = lb.get_leaderboard("pong")
        assert len(result) == 1
        assert result[0]["username"] == "alice"
        assert result[0]["score"] == 42

    def test_top_n_limits_results(self, load_leaderboard):
        sessions = [make_session("pong", f"player{i}", i * 10) for i in range(1, 8)]
        lb = load_leaderboard(sessions)
        result = lb.get_leaderboard("pong", top_n=3)
        assert len(result) == 3

    def test_sorted_highest_first(self, load_leaderboard):
        sessions = [
            make_session("pong", "alice", 30),
            make_session("pong", "bob",   80),
            make_session("pong", "carol", 50),
        ]
        lb = load_leaderboard(sessions)
        result = lb.get_leaderboard("pong")
        scores = [r["score"] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_result_contains_username_and_score_keys(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 10)])
        result = lb.get_leaderboard("pong")
        assert "username" in result[0]
        assert "score" in result[0]

    def test_invalid_sort_by_falls_back_to_best_score(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 99)])
        result = lb.get_leaderboard("pong", sort_by="invalid_mode")
        assert len(result) == 1
        assert result[0]["score"] == 99

    def test_sort_by_total_score(self, load_leaderboard):
        # alice plays twice (total 150), bob plays once (score 100)
        sessions = [
            make_session("pong", "alice", 50),
            make_session("pong", "alice", 100),
            make_session("pong", "bob",   100),
        ]
        lb = load_leaderboard(sessions)
        result = lb.get_leaderboard("pong", sort_by="total_score")
        assert result[0]["username"] == "alice"
        assert result[0]["score"] == 150

    def test_sort_by_play_time(self, load_leaderboard):
        sessions = [
            make_session("pong", "alice", play_time=300),
            make_session("pong", "bob",   play_time=120),
        ]
        lb = load_leaderboard(sessions)
        result = lb.get_leaderboard("pong", sort_by="play_time")
        assert result[0]["username"] == "alice"

    def test_best_score_uses_max_not_latest(self, load_leaderboard):
        # alice's first game is her best; second game has lower score
        sessions = [
            make_session("pong", "alice", 200),
            make_session("pong", "alice", 50),
        ]
        lb = load_leaderboard(sessions)
        result = lb.get_leaderboard("pong", sort_by="best_score")
        assert result[0]["score"] == 200

    def test_multiple_games_isolated(self, load_leaderboard):
        sessions = [
            make_session("pong",    "alice", 100),
            make_session("tetris",  "bob",   200),
        ]
        lb = load_leaderboard(sessions)
        pong_result   = lb.get_leaderboard("pong")
        tetris_result = lb.get_leaderboard("tetris")
        assert len(pong_result)   == 1
        assert len(tetris_result) == 1
        assert pong_result[0]["username"]   == "alice"
        assert tetris_result[0]["username"] == "bob"

    def test_default_top_n_is_ten(self, load_leaderboard):
        sessions = [make_session("pong", f"p{i}", i) for i in range(1, 16)]
        lb = load_leaderboard(sessions)
        assert len(lb.get_leaderboard("pong")) == 10


# ===========================================================================
# get_own_rank
# ===========================================================================

class TestGetOwnRank:

    def test_rank_of_only_player_is_one(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 100)])
        assert lb.get_own_rank("pong", "alice") == 1

    def test_top_player_is_rank_one(self, load_leaderboard):
        sessions = [
            make_session("pong", "alice", 100),
            make_session("pong", "bob",   50),
            make_session("pong", "carol", 10),
        ]
        lb = load_leaderboard(sessions)
        assert lb.get_own_rank("pong", "alice") == 1

    def test_last_place_rank(self, load_leaderboard):
        sessions = [
            make_session("pong", "alice", 100),
            make_session("pong", "bob",   50),
            make_session("pong", "carol", 10),
        ]
        lb = load_leaderboard(sessions)
        assert lb.get_own_rank("pong", "carol") == 3

    def test_unknown_player_returns_none(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 50)])
        assert lb.get_own_rank("pong", "ghost") is None

    def test_unknown_game_returns_none(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 50)])
        assert lb.get_own_rank("unknown_game", "alice") is None

    def test_rank_with_invalid_sort_by(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 75)])
        # Falls back to best_score; alice should still be rank 1
        assert lb.get_own_rank("pong", "alice", sort_by="bogus") == 1

    def test_rank_by_total_score(self, load_leaderboard):
        sessions = [
            make_session("pong", "alice", 50),
            make_session("pong", "alice", 60),  # total 110
            make_session("pong", "bob",   200), # total 200
        ]
        lb = load_leaderboard(sessions)
        assert lb.get_own_rank("pong", "bob",   sort_by="total_score") == 1
        assert lb.get_own_rank("pong", "alice", sort_by="total_score") == 2


# ===========================================================================
# get_players_in_score_range
# ===========================================================================

class TestGetPlayersInScoreRange:

    def test_returns_list(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 50)])
        assert isinstance(lb.get_players_in_score_range("pong", 0, 100), list)

    def test_empty_for_unknown_game(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 50)])
        assert lb.get_players_in_score_range("unknown", 0, 100) == []

    def test_exact_boundary_included(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 50)])
        result = lb.get_players_in_score_range("pong", 50, 50)
        assert len(result) == 1
        assert result[0]["username"] == "alice"

    def test_out_of_range_excluded(self, load_leaderboard):
        sessions = [
            make_session("pong", "alice", 10),
            make_session("pong", "bob",   90),
        ]
        lb = load_leaderboard(sessions)
        result = lb.get_players_in_score_range("pong", 20, 80)
        usernames = [r["username"] for r in result]
        assert "alice" not in usernames
        assert "bob"   not in usernames

    def test_results_sorted_descending(self, load_leaderboard):
        sessions = [
            make_session("pong", "alice", 30),
            make_session("pong", "bob",   70),
            make_session("pong", "carol", 50),
        ]
        lb = load_leaderboard(sessions)
        result = lb.get_players_in_score_range("pong", 0, 100)
        scores = [r["score"] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_partial_range(self, load_leaderboard):
        sessions = [
            make_session("pong", f"p{i}", i * 20) for i in range(1, 6)
        ]
        lb = load_leaderboard(sessions)
        # scores: 20,40,60,80,100 — range 40-80 gives 3 players
        result = lb.get_players_in_score_range("pong", 40, 80)
        assert len(result) == 3

    def test_contains_username_and_score(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 55)])
        result = lb.get_players_in_score_range("pong", 0, 100)
        assert "username" in result[0]
        assert "score"    in result[0]


# ===========================================================================
# get_all_games
# ===========================================================================

class TestGetAllGames:

    def test_returns_list(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 10)])
        assert isinstance(lb.get_all_games(), list)

    def test_empty_when_no_sessions(self, load_leaderboard):
        lb = load_leaderboard([])
        assert lb.get_all_games() == []

    def test_single_game(self, load_leaderboard):
        lb = load_leaderboard([make_session("pong", "alice", 10)])
        assert "pong" in lb.get_all_games()

    def test_multiple_games(self, load_leaderboard):
        sessions = [
            make_session("pong",   "alice", 10),
            make_session("tetris", "bob",   20),
        ]
        lb = load_leaderboard(sessions)
        games = lb.get_all_games()
        assert "pong"   in games
        assert "tetris" in games

    def test_no_duplicate_games(self, load_leaderboard):
        sessions = [
            make_session("pong", "alice", 10),
            make_session("pong", "bob",   20),
        ]
        lb = load_leaderboard(sessions)
        games = lb.get_all_games()
        assert games.count("pong") == 1


# ===========================================================================
# refresh
# ===========================================================================

class TestRefresh:

    def test_refresh_adds_new_player(self, load_leaderboard, monkeypatch):
        lb = load_leaderboard([make_session("pong", "alice", 50)])

        new_session = make_session("pong", "bob", 80)
        monkeypatch.setattr(lb.memory, "new_sessions", lambda: [new_session])

        lb.refresh()
        result = lb.get_leaderboard("pong")
        usernames = [r["username"] for r in result]
        assert "bob" in usernames

    def test_refresh_updates_existing_player_total(self, load_leaderboard, monkeypatch):
        lb = load_leaderboard([make_session("pong", "alice", 50)])

        new_session = make_session("pong", "alice", 60)
        monkeypatch.setattr(lb.memory, "new_sessions", lambda: [new_session])

        lb.refresh()
        result = lb.get_leaderboard("pong", sort_by="total_score")
        assert result[0]["score"] == 110  # 50 + 60

    def test_refresh_updates_best_score(self, load_leaderboard, monkeypatch):
        lb = load_leaderboard([make_session("pong", "alice", 50)])

        new_session = make_session("pong", "alice", 200)
        monkeypatch.setattr(lb.memory, "new_sessions", lambda: [new_session])

        lb.refresh()
        result = lb.get_leaderboard("pong", sort_by="best_score")
        assert result[0]["score"] == 200

    def test_refresh_does_not_lower_best_score(self, load_leaderboard, monkeypatch):
        lb = load_leaderboard([make_session("pong", "alice", 200)])

        new_session = make_session("pong", "alice", 10)
        monkeypatch.setattr(lb.memory, "new_sessions", lambda: [new_session])

        lb.refresh()
        result = lb.get_leaderboard("pong", sort_by="best_score")
        assert result[0]["score"] == 200

    def test_refresh_adds_new_game(self, load_leaderboard, monkeypatch):
        lb = load_leaderboard([make_session("pong", "alice", 50)])

        new_session = make_session("tetris", "bob", 100)
        monkeypatch.setattr(lb.memory, "new_sessions", lambda: [new_session])

        lb.refresh()
        assert "tetris" in lb.get_all_games()

    def test_refresh_skips_incomplete_sessions(self, load_leaderboard, monkeypatch):
        lb = load_leaderboard([make_session("pong", "alice", 50)])

        bad_sessions = [
            {"game": "pong"},          # missing username
            {"username": "ghost"},     # missing game
            {},                        # missing both
        ]
        monkeypatch.setattr(lb.memory, "new_sessions", lambda: bad_sessions)

        lb.refresh()
        # Only alice should exist; no ghost added
        result = lb.get_leaderboard("pong")
        assert all(r["username"] == "alice" for r in result)

    def test_refresh_with_no_new_sessions(self, load_leaderboard, monkeypatch):
        lb = load_leaderboard([make_session("pong", "alice", 50)])
        monkeypatch.setattr(lb.memory, "new_sessions", lambda: [])

        lb.refresh()
        assert lb.get_leaderboard("pong")[0]["username"] == "alice"