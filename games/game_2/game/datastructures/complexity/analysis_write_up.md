<<<<<<< HEAD
# Sparse Matrix Complexity Analysis
 
**Name:** Jude Hageman
**Date:** 4/12/2026
**Implementation:** COO (Coordinate List)
 
---
 
## Overview
 
My implementation uses a COO (Coordinate List) format backed by a custom `ArrayList`. Each non-default entry is stored as a `(row, col, value)` triple appended to the list. This is a natural fit for a sparse tile map because the map is mostly one default tile type (e.g., empty/water), and individual tiles are read and written one at a time rather than in bulk row operations. The main trade-off is that lookup and update both require a linear scan through stored entries, whereas a hash-based (DOK) approach would give O(1) average access at the cost of more complex bookkeeping.
 
---
 
## Time Complexity
 
| Operation | My SparseMatrix | scipy sparse (CSR) | numpy dense |
|-----------|-------------------|--------------------|-------------|
| `set(r, c, v)` | O(nnz) | O(nnz) amortised | O(1) |
| `get(r, c)` | O(nnz) | O(log nnz) | O(1) |
| `items()` iteration | O(nnz) | O(nnz) | O(n²) |
| `multiply(other)` | O(nnz²) | O(nnz²/n) | O(n³) |
 
*nnz = number of non-zero entries, n = matrix dimension side length*
 
**`set`:** The list must be scanned in full to check whether the position already exists before inserting or updating, so cost grows with the number of stored entries.
 
**`get`:** Same linear scan — in the worst case the entry is at the end of the list or absent entirely.
 
**`items()`:** Each stored triple is yielded once with no extra work, so cost is exactly proportional to nnz.
 
**`multiply`:** For every entry in `self` we scan all entries of `other` looking for matching `c1 == r2` pairs, giving O(nnz_A × nnz_B) in the worst case. scipy exploits CSR's sorted row structure to skip entire rows, which is why it beats our implementation on larger inputs.
 
---
 
## Benchmark Results
 
Run `sparse_matrix_complexity.py` and paste the output here:
 
```
Matrix size : 500×500   non-zero entries: 250   density: 0.100%
Get accesses: 1000   Multiply size: 100×100 with 20 nnz

  Operation                     Your Sparse      scipy CSR    numpy dense
  --------------------------------------------------------------
  build (set)                      3.64 ms       1.23 ms      134.8 µs
  get (1000 random)               23.60 ms      11.87 ms      198.5 µs
  items() iteration                27.6 µs       2.59 ms      45.26 ms
  multiply (100×100)               55.4 µs      148.7 µs      741.6 µs
```
 
---
 
## Space Complexity
 
| Representation | Space Used |
|----------------|-----------|
| Dense n×n      | O(n²)     |
| My sparse    | O(nnz)    |
 
The COO list stores exactly one tuple per non-default entry, so memory scales with nnz rather than the full grid size.
 
**Break-even density:** each COO entry holds 3 integers vs. 1 for a dense cell, so the sparse representation uses more memory once nnz > n²/3, i.e., when the matrix is more than roughly **33% full**. For a tile map that is 90%+ default tiles this is never a concern in practice.
 
---
 
## Observations
 
1. scipy is noticeably faster for `get` and `multiply` because CSR keeps entries sorted by row, allowing binary search and row-skipping; our COO list must scan from the beginning every time.
2. Sparse representations are faster than dense ones when nnz << n², because dense iteration always pays the full O(n²) cost regardless of how many cells are interesting.
3. The per-entry overhead of storing a Python tuple and going through `ArrayList` is visible compared to numpy's contiguous C arrays, especially for the `get` microbenchmark — even a single lookup involves a Python-level loop.
 
---
 
## Conclusions
 
COO is simple to implement and perfectly adequate for a read-heavy, write-light tile map where nnz stays well below n²/3. For workloads that require frequent random access or large matrix multiplications, a hash-based (DOK) or CSR representation would be worth the added complexity. The experiment made it clear that algorithmic structure (sorted rows in CSR) matters more than raw language speed once the matrix grows large.
 
---
 
## References
 
- scipy sparse matrix documentation: https://docs.scipy.org/doc/scipy/reference/sparse.html
||||||| 82bc39c
=======
# Written Analysis of Results

## Expected Results
For time complexity, adding a waypoint is expected to be O(1) due to a reference to the tail pointer being maintained, which allows for new nodes to be appended directly to the end of the patrol path, bypassing traversal of the list. Additionally, getting the next waypoint is expected to be O(1) since it advances the current pointer to the node next to it. The space complexity is expected to be O(n) because each new waypoint added requires memory for a node that contains several pieces of data.

## Comparisons
The measured results confirm that adding a waypoint and getting the next waypoint are done in constant time, O(1), which is as expected. Additonally, the space complexity showed linear, O(n), scaling. For example, adding 1,000,000 waypoints consumed 48 MB which is exactly 10 times the memory that was required when adding 100,000 waypoints.

## Discrepancies
There are discrepancies at very small values of n for the time complexity, which is due to execution overhead in Python. The values at larger values of n after the startup costs are much more representative.
>>>>>>> origin/main
