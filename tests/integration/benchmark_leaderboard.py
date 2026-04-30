"""
benchmark_leaderboard.py
Measures real execution time of every leaderboard function with dummy data
across increasing player counts (up to 5,000) and saves a chart.

HOW TO RUN
----------
Place this file anywhere in your project, then:

    python benchmark_leaderboard.py

Requirements: matplotlib  (pip install matplotlib)
"""

import sys
import types
import time
import random
import string
import importlib.util
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ---------------------------------------------------------------------------
# Configuration — adjust paths if your layout differs
# ---------------------------------------------------------------------------

# Root of the py_server package (contains leaderboards.py, data_structures/, etc.)
PROJECT_ROOT = Path(__file__).parent.parent.parent / "py_server"

# Path to the leaderboard module itself
LEADERBOARD_PATH = PROJECT_ROOT / "leaderboards.py"

# Benchmark settings
GAME  = "benchmark_game"
SIZES = [10, 50, 100, 250, 500, 1000, 2000, 3500, 5000]
RUNS  = 5    # repetitions per size (averaged)

# ---------------------------------------------------------------------------
# Make sure the data-structure packages are importable
# ---------------------------------------------------------------------------

for extra in [
    PROJECT_ROOT / "data_structures",
    PROJECT_ROOT / "algorithms" / "sorting",
]:
    p = str(extra)
    if p not in sys.path:
        sys.path.insert(0, p)

# ---------------------------------------------------------------------------
# Helper: fresh leaderboard import with controlled memory.sessions
# ---------------------------------------------------------------------------

def load_lb(sessions, extra_new=None):
    """
    Reload leaderboard with `sessions` as the startup session list.
    `extra_new` is what memory.new_sessions() will return (used by refresh()).
    """
    # Evict any cached copy so module-level init code re-runs
    for key in list(sys.modules.keys()):
        if "leaderboard" in key:
            del sys.modules[key]

    fake_memory = types.ModuleType("memory")
    fake_memory.sessions = sessions
    fake_memory.new_sessions = lambda: (extra_new or [])
    sys.modules["memory"] = fake_memory

    spec = importlib.util.spec_from_file_location("leaderboard", LEADERBOARD_PATH)
    lb   = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lb)
    return lb

# ---------------------------------------------------------------------------
# Dummy-data generation
# ---------------------------------------------------------------------------

def random_username(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))

def make_sessions(n):
    """Return n sessions for GAME with unique usernames."""
    seen, out = set(), []
    while len(out) < n:
        u = random_username()
        if u not in seen:
            seen.add(u)
            out.append({
                "game":             GAME,
                "username":         u,
                "individual_score": random.randint(0, 10_000),
                "game_time":        random.randint(30, 3_600),
            })
    return out

# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------

def measure(fn, runs=RUNS):
    """Return mean wall-clock time in seconds over `runs` calls."""
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return sum(times) / len(times)

# ---------------------------------------------------------------------------
# Run benchmarks
# ---------------------------------------------------------------------------

results = {k: [] for k in [
    "get_leaderboard",
    "get_own_rank",
    "get_players_in_score_range",
    "get_all_games",
    "refresh",
]}

print(f"Benchmarking leaderboard functions")
print(f"Player counts : {SIZES}")
print(f"Runs per size : {RUNS}\n")

for n in SIZES:
    sessions = make_sessions(n)
    mid_user = sessions[n // 2]["username"]   # a player guaranteed to exist
    new_sess = [make_sessions(1)[0]]           # one brand-new session for refresh()

    lb = load_lb(sessions, extra_new=new_sess)

    t_gl  = measure(lambda: lb.get_leaderboard(GAME, top_n=10))
    t_gor = measure(lambda: lb.get_own_rank(GAME, mid_user))
    t_rng = measure(lambda: lb.get_players_in_score_range(GAME, 2_000, 8_000))
    t_ag  = measure(lambda: lb.get_all_games())

    # refresh() re-imports to let module-level init re-run — use fewer reps
    def bench_refresh():
        lb2 = load_lb(sessions, extra_new=new_sess)
        lb2.refresh()

    t_ref = measure(bench_refresh, runs=3)

    results["get_leaderboard"].append(t_gl   * 1000)
    results["get_own_rank"].append(t_gor     * 1000)
    results["get_players_in_score_range"].append(t_rng * 1000)
    results["get_all_games"].append(t_ag     * 1000)
    results["refresh"].append(t_ref          * 1000)

    print(
        f"  n={n:>5}  "
        f"leaderboard={t_gl*1000:.3f}ms  "
        f"rank={t_gor*1000:.3f}ms  "
        f"range={t_rng*1000:.3f}ms  "
        f"all_games={t_ag*1000:.3f}ms  "
        f"refresh={t_ref*1000:.3f}ms"
    )

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

COLORS = {
    "get_leaderboard":            "#378ADD",
    "get_own_rank":               "#D85A30",
    "get_players_in_score_range": "#1D9E75",
    "get_all_games":              "#BA7517",
    "refresh":                    "#7F77DD",
}
LABELS = {
    "get_leaderboard":            "get_leaderboard()",
    "get_own_rank":               "get_own_rank()",
    "get_players_in_score_range": "get_players_in_score_range()",
    "get_all_games":              "get_all_games()",
    "refresh":                    "refresh()",
}
DASHES = {
    "get_leaderboard":            (None, None),
    "get_own_rank":               (6, 2),
    "get_players_in_score_range": (3, 2),
    "get_all_games":              (1, 2),
    "refresh":                    (8, 3),
}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle(
    "Leaderboard benchmark — BST + HashTable backend",
    fontsize=13, fontweight="500", y=1.01,
)

for fn, times in results.items():
    color        = COLORS[fn]
    label        = LABELS[fn]
    dash, gap    = DASHES[fn]
    linestyle    = (0, (dash, gap)) if dash else "solid"
    for ax in axes:
        ax.plot(
            SIZES, times,
            color=color, label=label,
            linestyle=linestyle, linewidth=2,
            marker="o", markersize=4,
        )

for ax, (xlog, ylog), title in zip(
    axes,
    [(False, False), (True, True)],
    ["Linear scale", "Log-log scale"],
):
    ax.set_title(title, fontsize=11, fontweight="500")
    ax.set_xlabel("Number of players (n)", fontsize=10)
    ax.set_ylabel("Time (ms)", fontsize=10)
    if xlog: ax.set_xscale("log")
    if ylog: ax.set_yscale("log")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.tick_params(labelsize=9)
    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda v, _: f"{int(v):,}")
    )

axes[0].legend(fontsize=9, framealpha=0.85)
fig.tight_layout()

out = Path("benchmark_results.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved → {out.resolve()}")