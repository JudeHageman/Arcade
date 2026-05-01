"""
benchmark_da.py
Measures real execution time of DynamicArray operations
across increasing sizes.

HOW TO RUN
----------
    pip install matplotlib
    python benchmark_da.py

Saves benchmark_da.png next to this file.
"""

import time
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from dynamic_array import ArrayList


# ---------------------------------------------------------------------------
# Sizes & Config
# ---------------------------------------------------------------------------

SIZES = [10, 50, 100, 250, 500, 1000, 2000, 3500, 5000, 7500, 10000]
RUNS = 20

# ---------------------------------------------------------------------------
# Benchmark: ArrayList
# ---------------------------------------------------------------------------

al_append_times = []
al_index_times  = []
al_remove_times = []

print("Benchmarking ArrayList...")
for n in SIZES:
    t_append = t_index = t_remove = 0.0

    for _ in range(RUNS):
        arr = ArrayList(initial_capacity=16)
        data = [random.randint(0, 100_000) for _ in range(n)]

        # append
        start = time.perf_counter()
        for v in data:
            arr.append(v)
        t_append += time.perf_counter() - start

        # __getitem__ (random access)
        idx = random.randint(0, n - 1)
        start = time.perf_counter()
        _ = arr[idx]
        t_index += time.perf_counter() - start

        # remove (search + shift)
        val = random.choice(data)
        start = time.perf_counter()
        arr.remove(val)
        t_remove += time.perf_counter() - start

    al_append_times.append((t_append / RUNS) * 1_000_000)
    al_index_times.append((t_index  / RUNS) * 1_000_000)
    al_remove_times.append((t_remove / RUNS) * 1_000_000)
    print(f"  ArrayList  n={n:6,} done")

# ---------------------------------------------------------------------------
# Plot
#   ArrayList  (linear | log-log)
# ---------------------------------------------------------------------------

BLUE   = "#378ADD"
ORANGE = "#D85A30"
GREEN  = "#2EAD6E"

fig, axes = plt.subplots(1, 2, figsize=(14, 10))
fig.suptitle("Data Structure Performance Benchmark", fontsize=14, fontweight="600", y=1.01)

def plot_da(ax_lin, ax_log, series, title):
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

plot_da(
    axes[0], axes[1],
    [
        ("Total Append Time",       al_append_times, BLUE),
        ("Single Index (get) Time", al_index_times,  ORANGE),
        ("Single Remove Time",      al_remove_times, GREEN),
    ],
    "ArrayList",
)

fig.tight_layout()

out = Path(__file__).parent / "benchmark_da.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved → {out.resolve()}")