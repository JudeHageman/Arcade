import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "py_server")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_structures")))

import leaderboards
from hash_table import HashTable
from bst import BST


def _load_fixture():
    """Load a fixed leaderboard fixture for integration tests."""
    leaderboards._trees = HashTable()
    leaderboards._raw = HashTable()
    leaderboards._team_trees = HashTable()
    leaderboards._team_raw = HashTable()

    game_name = "island"
    game_trees = HashTable()
    for mode in leaderboards.PLAYER_MODES:
        game_trees.put(mode, BST())
    leaderboards._trees.put(game_name, game_trees)

    # Player stats fixture
    entries = (
        ("alice", {"best_score": 90, "total_score": 200, "play_time": 300}),
        ("bob", {"best_score": 120, "total_score": 180, "play_time": 200}),
        ("cara", {"best_score": 70, "total_score": 260, "play_time": 400}),
    )
    for username, stats in entries:
        game_trees.get("best_score").insert(leaderboards.LeaderboardEntry(stats["best_score"], username))
        game_trees.get("total_score").insert(leaderboards.LeaderboardEntry(stats["total_score"], username))
        game_trees.get("play_time").insert(leaderboards.LeaderboardEntry(stats["play_time"], username))

    # Team fixture
    team_tree = BST()
    team_tree.insert(leaderboards._team_entry(500, "pink"))
    team_tree.insert(leaderboards._team_entry(300, "blue"))
    leaderboards._team_trees.put(game_name, team_tree)
    leaderboards.memory.accounts = {
        "alice": {"team": "pink"},
        "bob": {"team": "blue"},
        "cara": {"team": "pink"},
    }

    return game_name


def test_leaderboard_flow():
    game_name = _load_fixture()

    rows = leaderboards.get_leaderboard(game_name, top_n=2, sort_by="best_score")
    assert len(rows) == 2, "Should return top 2 rows"
    assert rows[0]["username"] == "bob", "Highest best_score should rank first"
    assert rows[1]["username"] == "alice", "Second highest best_score should rank second"
    rank = leaderboards.get_own_rank(game_name, "alice", sort_by="best_score")
    assert rank == 2, "Alice should be rank 2 by best_score"
    rank = leaderboards.get_own_rank(game_name, "alice", sort_by="team_score")
    assert rank == 1, "Pink team should be rank 1 by team_score"
    rows = leaderboards.get_players_in_score_range(game_name, low=80, high=130, sort_by="best_score")
    usernames = [row["username"] for row in rows]
    assert usernames == ["bob", "alice"], "Range query should return sorted players in descending score order"

def run_all_tests():
    test_leaderboard_flow()
    print("\nAll tests passed.")


if __name__ == "__main__":
    run_all_tests()
