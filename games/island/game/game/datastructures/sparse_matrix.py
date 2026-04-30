"""
sparse_matrix.py - Sparse Matrix implementation

A sparse matrix stores only non-default entries, saving memory when most
cells share the same value (like -1 in a tile map).

Choose one of three backing representations:

  Option A — DOK (Dictionary of Keys): {(row, col): value}
    Requires implementing HashTable in hash_table.py.
    Do not use Python's built-in dict or set.

  Option B — COO (Coordinate List): list of (row, col, value) triples
    Use your ArrayList from Lab 3. Do not use Python's built-in list.

  Option C — CSR (Compressed Sparse Row): three parallel arrays
    row_ptr, col_idx, values. Most efficient for row-wise access.

All three options must satisfy the same interface.

Author: Minju Seo 
Date:   2026-04-09
Lab:    Lab 6 - Sparse World Map
"""


# =============================================================================
# Do not modify SparseMatrixBase.
# =============================================================================

class SparseMatrixBase:
    """Interface definition. Your SparseMatrix must inherit from this."""

    def __init__(self, rows=None, cols=None, default=0):
        self.rows    = rows
        self.cols    = cols
        self.default = default

    def set(self, row, col, value):
        raise NotImplementedError

    def get(self, row, col):
        raise NotImplementedError

    def items(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def multiply(self, other):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


# =============================================================================
# Your implementation goes here.
# =============================================================================

from datastructures.hash_table import HashTable

class SparseMatrix(SparseMatrixBase):

    def __init__(self, rows=None, cols=None, default=0):
        super().__init__(rows, cols, default)
        # Use our custom HashTable for storage
        self.data = HashTable()

    def set(self, row, col, value):
        """Store value or remove if it is default."""
        key = (row, col)
        if value == self.default:
            # If value is default, remove entry to save memory
            if key in self.data:
                self.data.delete(key)
        else:
            self.data.set(key, value)

    def get(self, row, col):
        """Return stored value or the default."""
        return self.data.get((row, col), self.default)

    def items(self):
        """Yield ((row, col), value) tuples."""
        # Delegate to HashTable's items() generator
        return self.data.items()

    def __len__(self):
        """Return the number of non-default entries."""
        return len(self.data)

    def multiply(self, other):
        """Matrix multiplication: result = self * other."""
        # Basic dimension check
        if self.cols is not None and other.rows is not None:
            if self.cols != other.rows:
                raise ValueError("Incompatible dimensions for multiplication.")

        # Result matrix usually defaults to 0 for math operations
        result = SparseMatrix(rows=self.rows, cols=other.cols, default=0)

        # Optimization: Only iterate through non-default entries
        for (r1, c1), v1 in self.items():
            for (r2, c2), v2 in other.items():
                if c1 == r2: # When inner dimensions match (k index)
                    current_val = result.get(r1, c2)
                    result.set(r1, c2, current_val + (v1 * v2))
        return result

    def __str__(self):
        """Return a human-readable summary."""
        return f"SparseMatrix(rows={self.rows}, cols={self.cols}, nnz={len(self)})"