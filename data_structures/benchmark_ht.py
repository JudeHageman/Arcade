"""
benchmark_ht.py
Measures real execution time of HashTable operations
across increasing sizes.

HOW TO RUN
----------
    pip install matplotlib
    python benchmark_ht.py

Saves benchmark_ht.png next to this file.
"""

import time
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from hash_table import HashTable

# ---------------------------------------------------------------------------
# Sizes & Config
# ---------------------------------------------------------------------------

SIZES = [10, 50, 100, 250, 500, 1000, 2000, 3500, 5000, 7500, 10000, 15000, 25000, 50000, 75000, 100000]
RUNS = 20

# ---------------------------------------------------------------------------
# Benchmark: HashTable
# ---------------------------------------------------------------------------

ht_put_times    = []
ht_get_times    = []
ht_remove_times = []

print("Benchmarking HashTable...")
for n in SIZES:
    t_put = t_get = t_remove = 0.0

    for _ in range(RUNS):
        ht   = HashTable(capacity=67)
        keys = [random.randint(0, 100_000) for _ in range(n)]
        vals = [random.randint(0, 100_000) for _ in range(n)]

        # put
        start = time.perf_counter()
        for k, v in zip(keys, vals):
            ht.put(k, v)
        t_put += time.perf_counter() - start

        # get (random existing key)
        k = random.choice(keys)
        start = time.perf_counter()
        ht.get(k)
        t_get += time.perf_counter() - start

        # remove (random existing key)
        k = random.choice(keys)
        start = time.perf_counter()
        ht.remove(k)
        t_remove += time.perf_counter() - start

    ht_put_times.append((t_put    / RUNS) * 1_000_000)
    ht_get_times.append((t_get    / RUNS) * 1_000_000)
    ht_remove_times.append((t_remove / RUNS) * 1_000_000)
    print(f"  HashTable  n={n:6,} done")

# ---------------------------------------------------------------------------
# Plot
#   HashTable  (linear | log-log)
# ---------------------------------------------------------------------------

BLUE   = "#378ADD"
ORANGE = "#D85A30"
GREEN  = "#2EAD6E"

fig, axes = plt.subplots(1, 2, figsize=(14, 10))
fig.suptitle("Data Structure Performance Benchmark", fontsize=14, fontweight="600", y=1.01)

def plot_ht(ax_lin, ax_log, series, title):
    for label, times, color in series:
        for ax in (ax_lin, ax_log):
            ax.plot(SIZES, times, color=color, label=label, marker="o", markersize=4)
    for ax, (xlog, ylog), scale in zip(
        (ax_lin, ax_log),
        [(False, False), (True, True)],
        ["Linear Scale", "Log-Log Scale"],
    ):
        ax.set_title(f"{title} — {scale}", fontsize=11)
        ax.set_xlabel("Number of Elements (n)")
        ax.set_ylabel("Time (µs)")
        if xlog: ax.set_xscale("log")
        if ylog: ax.set_yscale("log")
        ax.grid(True, which="both", linestyle="--", alpha=0.45)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
        ax.legend(fontsize=8)

plot_ht(
    axes[0], axes[1],
    [
        ("Total Put Time",      ht_put_times,    BLUE),
        ("Single Get Time",     ht_get_times,    ORANGE),
        ("Single Remove Time",  ht_remove_times, GREEN),
    ],
    "HashTable",
)
fig.tight_layout()

out = Path(__file__).parent / "benchmark_ht.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved → {out.resolve()}")