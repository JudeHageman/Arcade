"""
sparse_matrix_complexity.py - Performance analysis for SparseMatrix

Compare your SparseMatrix implementation to:
  - scipy.sparse (CSR format)
  - numpy dense matrix (numpy.ndarray)

Measure and report wall-clock time for:
  1. Building the matrix (set() calls)
  2. Random get() accesses
  3. items() full iteration
  4. multiply()

Run with:
    cd code/game/datastructures/complexity
    python sparse_matrix_complexity.py

Install dependencies if needed:
    pip install scipy numpy

Author: Jude Hageman
Date:   4/12/2026
Lab:    Lab 6 - Sparse World Map
"""

import time
import random
import sys
import os

try:
    from scipy.sparse import csr_matrix, lil_matrix
    import numpy as np
except ImportError:
    print("scipy/numpy not installed — run: pip install scipy numpy")
    sys.exit(1)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from datastructures.sparse_matrix import SparseMatrix


# ==========================================================================
# Config
# ==========================================================================

N          = 500    # matrix side length (N x N)
NNZ        = 250    # number of non-zero entries (~0.1% density)
GET_COUNT  = 1000   # number of random get() calls to time


def make_entries(n, nnz):
    """Return a list of (row, col, value) with no duplicate positions."""
    positions = random.sample([(r, c) for r in range(n) for c in range(n)], nnz)
    return [(r, c, random.randint(1, 100)) for r, c in positions]


def timer(fn):
    t0 = time.perf_counter()
    result = fn()
    return time.perf_counter() - t0, result


# ==========================================================================
# 1. Build
# ==========================================================================

def bench_build(entries):
    # --- Your SparseMatrix ---
    def build_sparse():
        m = SparseMatrix(rows=N, cols=N, default=0)
        for r, c, v in entries:
            m.set(r, c, v)
        return m

    # --- scipy LIL (mutable build format, then convert to CSR) ---
    def build_scipy():
        m = lil_matrix((N, N), dtype=int)
        for r, c, v in entries:
            m[r, c] = v
        return m.tocsr()

    # --- numpy dense ---
    def build_numpy():
        m = np.zeros((N, N), dtype=int)
        for r, c, v in entries:
            m[r, c] = v
        return m

    t_sparse, sm  = timer(build_sparse)
    t_scipy,  sci = timer(build_scipy)
    t_numpy,  npy = timer(build_numpy)
    return t_sparse, t_scipy, t_numpy, sm, sci, npy


# ==========================================================================
# 2. Random get
# ==========================================================================

def bench_get(sm, sci, npy, entries):
    # Reuse the positions we inserted so at least some are hits
    positions = [(r, c) for r, c, _ in entries]
    # Pad out to GET_COUNT with random positions
    while len(positions) < GET_COUNT:
        positions.append((random.randint(0, N-1), random.randint(0, N-1)))
    random.shuffle(positions)
    positions = positions[:GET_COUNT]

    t_sparse, _ = timer(lambda: [sm.get(r, c) for r, c in positions])
    t_scipy,  _ = timer(lambda: [sci[r, c]    for r, c in positions])
    t_numpy,  _ = timer(lambda: [npy[r, c]    for r, c in positions])
    return t_sparse, t_scipy, t_numpy


# ==========================================================================
# 3. Iteration (items)
# ==========================================================================

def bench_items(sm, sci, npy):
    # Your SparseMatrix
    t_sparse, _ = timer(lambda: list(sm.items()))

    # scipy: iterate non-zeros via .nonzero()
    def scipy_iter():
        rows, cols = sci.nonzero()
        return [(r, c, sci[r, c]) for r, c in zip(rows, cols)]
    t_scipy, _ = timer(scipy_iter)

    # numpy: iterate every cell (true dense iteration)
    t_numpy, _ = timer(lambda: [(r, c, npy[r, c])
                                 for r in range(N) for c in range(N)])
    return t_sparse, t_scipy, t_numpy


# ==========================================================================
# 4. Multiply
# ==========================================================================

def bench_multiply(entries):
    # Build two small-ish matrices so multiply doesn't take forever
    M = 100
    nnz_small = 20
    small_entries = random.sample(
        [(r, c) for r in range(M) for c in range(M)], nnz_small
    )
    vals = [(r, c, random.randint(1, 10)) for r, c in small_entries]

    def make_sm():
        m = SparseMatrix(rows=M, cols=M, default=0)
        for r, c, v in vals:
            m.set(r, c, v)
        return m

    sm_a = make_sm()
    sm_b = make_sm()

    sci_a = lil_matrix((M, M), dtype=int)
    sci_b = lil_matrix((M, M), dtype=int)
    for r, c, v in vals:
        sci_a[r, c] = v
        sci_b[r, c] = v
    sci_a = sci_a.tocsr()
    sci_b = sci_b.tocsr()

    npy_a = np.zeros((M, M), dtype=int)
    npy_b = np.zeros((M, M), dtype=int)
    for r, c, v in vals:
        npy_a[r, c] = v
        npy_b[r, c] = v

    t_sparse, _ = timer(lambda: sm_a.multiply(sm_b))
    t_scipy,  _ = timer(lambda: sci_a.dot(sci_b))
    t_numpy,  _ = timer(lambda: npy_a @ npy_b)
    return t_sparse, t_scipy, t_numpy


# ==========================================================================
# Report
# ==========================================================================

def fmt(t):
    if t < 1e-3:
        return f"{t*1e6:8.1f} µs"
    if t < 1:
        return f"{t*1e3:8.2f} ms"
    return f"{t:8.3f}  s"


def print_row(label, ts, tc, tn):
    print(f"  {label:<28} {fmt(ts)}   {fmt(tc)}   {fmt(tn)}")


if __name__ == '__main__':
    random.seed(42)
    entries = make_entries(N, NNZ)

    print(f"\nMatrix size : {N}×{N}   non-zero entries: {NNZ}   "
          f"density: {NNZ/(N*N)*100:.3f}%")
    print(f"Get accesses: {GET_COUNT}   Multiply size: 100×100 with 20 nnz\n")

    print(f"  {'Operation':<28} {'Your Sparse':>12}   {'scipy CSR':>12}   {'numpy dense':>12}")
    print("  " + "-" * 62)

    tb_s, tb_c, tb_n, sm, sci, npy = bench_build(entries)
    print_row("build (set)", tb_s, tb_c, tb_n)

    tg_s, tg_c, tg_n = bench_get(sm, sci, npy, entries)
    print_row(f"get ({GET_COUNT} random)", tg_s, tg_c, tg_n)

    ti_s, ti_c, ti_n = bench_items(sm, sci, npy)
    print_row("items() iteration", ti_s, ti_c, ti_n)

    tm_s, tm_c, tm_n = bench_multiply(entries)
    print_row("multiply (100×100)", tm_s, tm_c, tm_n)

    print()