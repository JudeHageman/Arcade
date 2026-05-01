"""
benchmark_pt.py
Measures real execution time of prefix trie operations,
specifically the insert() and search() methods for maintaining sorted leaderboards.
in server.py across increasing account-table sizes (up to 100,000).

HOW TO RUN
----------
    pip install matplotlib
    python benchmark_pt.py          # from Arcade/data_structures

Saves benchmark_pt.png next to this file.
"""

import time
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from prefix_trie import PrefixTrie
from dynamic_array import ArrayList
from hash_table import HashTable

# ---------------------------------------------------------------------------
# Benchmark Logic
# ---------------------------------------------------------------------------

SIZES = ArrayList(initial_capacity=16)
SIZES.extend([10, 50, 100, 250, 500, 1000, 2000, 3500, 5000, 7500, 10000, 15000, 25000, 50000, 75000, 100000])
RUNS = 20

results = HashTable()
results.put("insert", [])
results.put("search", [])

print("Starting benchmark...")
for n in SIZES:
    t_insert = 0
    t_search = 0 

    for _ in range(RUNS):
        trie = PrefixTrie()
        data = [str(random.randint(0, 100000)) for _ in range(n)]

        # Measure Insert
        start = time.perf_counter()
        for val in data:
            trie.insert(val)
        t_insert += (time.perf_counter() - start)

        # Measure Search (random value from inserted data)
        search_val = random.choice(data)
        start = time.perf_counter()
        trie.search(search_val)
        t_search += (time.perf_counter() - start)

    # Convert to microseconds (µs) and average
    results["insert"].append((t_insert / RUNS) * 1_000_000)
    results["search"].append((t_search / RUNS) * 1_000_000)
    print(f"Size {n:6,} processed.")

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

COLORS = {"insert": "#378ADD", "search": "#D85A30"}
LABELS = {"insert": "Total Time to Insert N elements", "search": "Single Search Time (search)"}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Prefix Trie Performance Benchmark", fontsize=13, fontweight="500", y=1.05)

for key in ("insert", "search"):
    times = results[key]
    for ax in axes:
        ax.plot(SIZES, times, color=COLORS[key], label=LABELS[key], marker="o", markersize=4)

for ax, (xlog, ylog), title in zip(axes, [(False, False), (True, True)], ["Linear Scale", "Log-Log Scale"]):
    ax.set_title(title)
    ax.set_xlabel("Number of Elements (n)")
    ax.set_ylabel("Time (µs)")
    if xlog: ax.set_xscale("log")
    if ylog: ax.set_yscale("log")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))

axes[0].legend()
fig.tight_layout()

out = Path(__file__).parent / "benchmark_pt.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved → {out.resolve()}")