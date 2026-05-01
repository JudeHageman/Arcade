"""
benchmark_ll.py
Measures real execution time of LinkedList operations:
  - add_last   (append to tail)
  - remove_first (pop from head)
  - mixed      (interleaved add/remove)

HOW TO RUN
----------
    pip install matplotlib --break-system-packages
    python benchmark_ll.py

Saves benchmark_ll.png next to this file.
"""

import time
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ---------------------------------------------------------------------------
# Inline LinkedList (no external file dependency)
# ---------------------------------------------------------------------------

class DoublyNode:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_last(self, value):
        new_node = DoublyNode(value)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

    def remove_first(self):
        if not self.head:
            return None
        val = self.head.value
        self.head = self.head.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None
        return val

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SIZES = [10, 50, 100, 250, 500, 1000, 2000, 3500, 5000, 7500, 10000, 15000, 25000, 50000, 75000, 100000]
RUNS  = 20

# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

add_last_times     = []
remove_first_times = []
mixed_times        = []

print("Benchmarking LinkedList...")
for n in SIZES:
    t_add = t_remove = t_mixed = 0.0

    for _ in range(RUNS):
        data = [random.randint(0, 100_000) for _ in range(n)]

        # --- Total add_last time for N elements ---
        ll = LinkedList()
        start = time.perf_counter()
        for v in data:
            ll.add_last(v)
        t_add += time.perf_counter() - start

        # --- Single remove_first (list already has N elements) ---
        start = time.perf_counter()
        ll.remove_first()
        t_remove += time.perf_counter() - start

        # --- Mixed: add N/2 then alternate add/remove for N/2 ops ---
        ll2 = LinkedList()
        half = n // 2
        for v in data[:half]:
            ll2.add_last(v)
        start = time.perf_counter()
        for i in range(half, n):
            if i % 2 == 0:
                ll2.add_last(data[i])
            else:
                ll2.remove_first()
        t_mixed += time.perf_counter() - start

    add_last_times.append((t_add    / RUNS) * 1_000_000)
    remove_first_times.append((t_remove / RUNS) * 1_000_000)
    mixed_times.append((t_mixed  / RUNS) * 1_000_000)
    print(f"  n={n:6,} done")

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

BLUE   = "#378ADD"
ORANGE = "#D85A30"
GREEN  = "#2EAD6E"

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("LinkedList Performance Benchmark", fontsize=14, fontweight="600", y=1.02)

series = [
    ("Total add_last Time (N elements)", add_last_times,     BLUE),
    ("Single remove_first Time",         remove_first_times, ORANGE),
    ("Mixed add/remove Time (N/2 ops)",  mixed_times,        GREEN),
]

for label, times, color in series:
    for ax in axes:
        ax.plot(SIZES, times, color=color, label=label, marker="o", markersize=4)

for ax, (xlog, ylog), title in zip(
    axes,
    [(False, False), (True, True)],
    ["Linear Scale", "Log-Log Scale"],
):
    ax.set_title(title)
    ax.set_xlabel("Number of Elements (n)")
    ax.set_ylabel("Time (µs)")
    if xlog: ax.set_xscale("log")
    if ylog: ax.set_yscale("log")
    ax.grid(True, which="both", linestyle="--", alpha=0.45)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))

axes[0].legend(fontsize=8)
fig.tight_layout()

out = Path(__file__).parent / "benchmark_ll.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved → {out.resolve()}")