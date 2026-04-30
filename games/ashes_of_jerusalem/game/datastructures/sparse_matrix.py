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

Author: Jude Hageman
Date:   4/12/2026
Lab:    Lab 6 - Sparse World Map
"""
from .array import ArrayList


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

class SparseMatrix(SparseMatrixBase):

    def __init__(self, rows=None, cols=None, default=0):
        super().__init__(rows, cols, default)
        self.data = ArrayList()

    def set(self, row, col, value):
        for i in range(len(self.data)):
            r, c, v = self.data[i]          # was: self.data.get(i)
            if r == row and c == col:
                if value == self.default:
                    self.data.remove(self.data[i])  # remove by value
                else:
                    self.data[i] = (row, col, value) # was: self.data.set(i, ...)
                return
        if value != self.default:
            self.data.append((row, col, value))

    def get(self, row, col):
        for i in range(len(self.data)):
            r, c, v = self.data[i]          # was: self.data.get(i)
            if r == row and c == col:
                return v
        return self.default

    def items(self):
        for i in range(len(self.data)):
            yield self.data[i]              # was: self.data.get(i)

    def __len__(self):
        return len(self.data)

    def multiply(self, other):
        if self.cols != other.rows:
            raise ValueError("Incompatible dimensions for multiplication")
        result = SparseMatrix(rows=self.rows, cols=other.cols, default=self.default)
        for r1, c1, v1 in self.items():
            for r2, c2, v2 in other.items():
                if c1 == r2:
                    current_value = result.get(r1, c2)
                    result.set(r1, c2, current_value + v1 * v2)
        return result

    def __str__(self):
        matrix_str = ""
        for r in range(self.rows):
            row_str = []
            for c in range(self.cols):
                row_str.append(str(self.get(r, c)))
            matrix_str += " ".join(row_str) + "\n"
        return matrix_str