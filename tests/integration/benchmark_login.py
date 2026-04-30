"""
benchmark_login.py
Measures real execution time of authenticate_account() and create_account()
in server.py across increasing account-table sizes (up to 5,000).

HOW TO RUN
----------
    pip install matplotlib
    python benchmark_login.py          # from Arcade/tests/integration/

Saves benchmark_login.png next to this file.
"""

import sys
import types
import time
import random
import string
import hashlib
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, mock_open

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent.parent / "py_server"
SERVER_PATH  = PROJECT_ROOT / "server.py"

for p in [str(PROJECT_ROOT), str(PROJECT_ROOT / "data_structures")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ---------------------------------------------------------------------------
# Benchmark settings
# ---------------------------------------------------------------------------

SIZES = [10, 50, 100, 250, 500, 1000, 2000, 3500, 5000]
RUNS  = 10   # averaged repetitions per measurement

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()

def random_username(length=8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))

def random_password(length=10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def measure(fn, runs=RUNS) -> float:
    """Return mean wall-clock time in seconds over `runs` calls."""
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return sum(times) / len(times)

# ---------------------------------------------------------------------------
# Load server with stubbed I/O
# ---------------------------------------------------------------------------

def load_server(tmp_path: Path):
    """
    Import server.py with:
      - websockets stubbed (no real network)
      - all sibling modules stubbed
      - data files pointing at tmp_path (no real disk reads)
    Returns the loaded server module with a clean accounts table.
    """
    for key in list(sys.modules.keys()):
        if key in ("server", "websockets", "websockets.exceptions"):
            del sys.modules[key]

    ws_mod = types.ModuleType("websockets")
    ws_exc = types.ModuleType("websockets.exceptions")
    class ConnectionClosed(Exception): pass
    ws_exc.ConnectionClosed = ConnectionClosed
    ws_mod.exceptions = ws_exc
    ws_mod.serve = MagicMock()
    sys.modules["websockets"] = ws_mod
    sys.modules["websockets.exceptions"] = ws_exc

    for mod_name in ("games", "leaderboards", "profile",
                     "match_history", "player_search", "memory"):
        m = types.ModuleType(mod_name)
        m.refresh = lambda: None
        sys.modules[mod_name] = m

    # Create empty stub files
    for fname in ("accounts.ndjson", "chats.ndjson", "sessions.ndjson", "games.ndjson"):
        (tmp_path / fname).write_text("")

    spec = importlib.util.spec_from_file_location("server", SERVER_PATH)
    srv  = importlib.util.module_from_spec(spec)
    with __import__("unittest.mock", fromlist=["mock_open", "patch"]).patch(
        "builtins.open", mock_open(read_data="")
    ):
        spec.loader.exec_module(srv)

    srv.accounts_file = tmp_path / "accounts.ndjson"
    srv.sessions_file = tmp_path / "sessions.ndjson"
    srv.chats_file    = tmp_path / "chats.ndjson"
    return srv

# ---------------------------------------------------------------------------
# Run benchmarks
# ---------------------------------------------------------------------------

import tempfile

results = {
    "authenticate_existing":  [],   # look up a user who IS in the table
    "authenticate_missing":   [],   # look up a user who is NOT in the table
    "authenticate_invalid_pw":[],   # user exists but wrong password
    "create_account":         [],   # insert a brand-new account
}

print(f"Benchmarking login functions up to {SIZES[-1]:,} accounts "
      f"({RUNS} runs per measurement)...\n")

for n in SIZES:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        srv = load_server(tmp_path)

        # Pre-populate the accounts table with n unique users
        usernames = []
        passwords = []
        seen = set()
        while len(usernames) < n:
            u = random_username()
            if u not in seen:
                seen.add(u)
                p = random_password()
                usernames.append(u)
                passwords.append(p)
                srv.accounts.put(u, {"password": hash_pw(p), "team": "default"})

        # Pick a target in the middle of the table
        mid          = n // 2
        target_user  = usernames[mid]
        target_pw    = passwords[mid]
        missing_user = "zzznotauser"          # guaranteed absent
        new_user     = f"newuser_{n}"         # for create benchmark

        t_exist  = measure(lambda: srv.authenticate_account(target_user,  target_pw))
        t_miss   = measure(lambda: srv.authenticate_account(missing_user, "anypass"))
        t_badpw  = measure(lambda: srv.authenticate_account(target_user,  "wrongpw"))
        t_create = measure(lambda: srv.create_account(new_user, hash_pw("benchpw"), "red"))

        results["authenticate_existing"].append(t_exist   * 1_000_000)
        results["authenticate_missing"].append(t_miss     * 1_000_000)
        results["authenticate_invalid_pw"].append(t_badpw * 1_000_000)
        results["create_account"].append(t_create         * 1_000_000)

        print(
            f"  n={n:>5}  "
            f"auth_existing={t_exist*1e6:.2f}µs  "
            f"auth_missing={t_miss*1e6:.2f}µs  "
            f"auth_badpw={t_badpw*1e6:.2f}µs  "
            f"create={t_create*1e6:.2f}µs"
        )

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

COLORS = {
    "authenticate_existing":   "#378ADD",
    "authenticate_missing":    "#D85A30",
    "authenticate_invalid_pw": "#1D9E75",
    "create_account":          "#7F77DD",
}
LABELS = {
    "authenticate_existing":   "authenticate — correct password",
    "authenticate_missing":    "authenticate — user not found",
    "authenticate_invalid_pw": "authenticate — wrong password",
    "create_account":          "create_account()",
}
DASHES = {
    "authenticate_existing":   (None, None),
    "authenticate_missing":    (6, 2),
    "authenticate_invalid_pw": (3, 2),
    "create_account":          (8, 3),
}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle(
    "Login benchmark — HashTable-backed accounts store",
    fontsize=13, fontweight="500", y=1.01,
)

for fn, times in results.items():
    ls = (0, (DASHES[fn][0], DASHES[fn][1])) if DASHES[fn][0] else "solid"
    for ax in axes:
        ax.plot(
            SIZES, times,
            color=COLORS[fn], label=LABELS[fn],
            linestyle=ls, linewidth=2,
            marker="o", markersize=4,
        )

for ax, (xlog, ylog), title in zip(
    axes,
    [(False, False), (True, True)],
    ["Linear scale", "Log-log scale"],
):
    ax.set_title(title, fontsize=11, fontweight="500")
    ax.set_xlabel("Number of registered accounts (n)", fontsize=10)
    ax.set_ylabel("Time (µs)", fontsize=10)
    if xlog: ax.set_xscale("log")
    if ylog: ax.set_yscale("log")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.tick_params(labelsize=9)
    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda v, _: f"{int(v):,}")
    )

axes[0].legend(fontsize=9, framealpha=0.85)
fig.tight_layout()

out = Path(__file__).parent / "benchmark_login.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved → {out.resolve()}")