"""
sparse_matrix_tests.py - Tests for SparseMatrix

Write tests for ALL methods of your SparseMatrix implementation.
You may use AI to help generate edge cases, but make sure you understand
every test before submitting.

Run with:
    cd code/game/datastructures/tests
    python sparse_matrix_tests.py

Author: Jude Hageman
Date:   4/12/2026
Lab:    Lab 6 - Sparse World Map
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.sparse_matrix import SparseMatrix


# ==========================================================================
# Helper
# ==========================================================================

def assert_equal(actual, expected, msg=""):
    if actual != expected:
        raise AssertionError(f"FAIL {msg}: expected {expected!r}, got {actual!r}")


# ==========================================================================
# get / set
# ==========================================================================

def test_set_and_get():
    """Values that were set should be retrievable at the same position."""
    m = SparseMatrix(rows=5, cols=5, default=0)
    m.set(1, 2, 99)
    assert_equal(m.get(1, 2), 99, "test_set_and_get")


def test_default_value():
    """Positions that were never set should return the default (0)."""
    m = SparseMatrix(rows=5, cols=5, default=0)
    assert_equal(m.get(0, 0), 0, "test_default_value: (0,0)")
    assert_equal(m.get(4, 4), 0, "test_default_value: (4,4)")


def test_custom_default():
    """A non-zero default should be returned for unset positions."""
    m = SparseMatrix(rows=3, cols=3, default=-1)
    assert_equal(m.get(0, 0), -1, "test_custom_default: unset cell")
    m.set(1, 1, 7)
    assert_equal(m.get(1, 1), 7,  "test_custom_default: set cell")
    assert_equal(m.get(2, 2), -1, "test_custom_default: still default")


def test_overwrite():
    """Setting a position twice should keep only the latest value."""
    m = SparseMatrix(rows=5, cols=5, default=0)
    m.set(2, 3, 10)
    m.set(2, 3, 42)
    assert_equal(m.get(2, 3), 42, "test_overwrite")


def test_set_to_default_removes_entry():
    """Setting a cell to the default value should remove the stored entry."""
    m = SparseMatrix(rows=5, cols=5, default=0)
    m.set(1, 1, 5)
    assert_equal(len(m), 1, "test_set_to_default_removes_entry: before reset")
    m.set(1, 1, 0)   # reset to default
    assert_equal(len(m), 0, "test_set_to_default_removes_entry: after reset")
    assert_equal(m.get(1, 1), 0, "test_set_to_default_removes_entry: get after reset")


# ==========================================================================
# __len__
# ==========================================================================

def test_len_empty():
    """A new matrix should have length 0."""
    m = SparseMatrix(rows=10, cols=10, default=0)
    assert_equal(len(m), 0, "test_len_empty")


def test_len_after_set():
    """len() should count only non-default entries."""
    m = SparseMatrix(rows=10, cols=10, default=0)
    m.set(0, 0, 1)
    m.set(1, 1, 2)
    m.set(2, 2, 3)
    assert_equal(len(m), 3, "test_len_after_set: three entries")
    m.set(1, 1, 0)   # remove one
    assert_equal(len(m), 2, "test_len_after_set: after removing one")


# ==========================================================================
# items()
# ==========================================================================

def test_items_empty():
    """items() on an empty matrix should yield nothing."""
    m = SparseMatrix(rows=3, cols=3, default=0)
    entries = list(m.items())
    assert_equal(len(entries), 0, "test_items_empty")


def test_items_yields_correct_entries():
    """items() should yield exactly the non-default (row, col, value) triples."""
    m = SparseMatrix(rows=5, cols=5, default=0)
    m.set(0, 1, 10)
    m.set(3, 4, 20)
    entries = list(m.items())
    assert_equal(len(entries), 2, "test_items_yields_correct_entries: count")
    # Check that both expected entries are present (order not guaranteed)
    values = {(r, c): v for r, c, v in entries}
    assert_equal(values.get((0, 1)), 10, "test_items_yields_correct_entries: (0,1)")
    assert_equal(values.get((3, 4)), 20, "test_items_yields_correct_entries: (3,4)")


def test_items_consistent_with_get():
    """Every (r, c) yielded by items() should match get(r, c)."""
    m = SparseMatrix(rows=10, cols=10, default=0)
    coords = [(0, 5), (3, 3), (7, 1), (9, 9)]
    for i, (r, c) in enumerate(coords):
        m.set(r, c, (i + 1) * 11)
    for r, c, v in m.items():
        assert_equal(m.get(r, c), v, f"test_items_consistent_with_get: ({r},{c})")


# ==========================================================================
# Large / memory
# ==========================================================================

def test_large_sparse():
    """A 1000×1000 matrix with 10 entries should store only 10 entries."""
    m = SparseMatrix(rows=1000, cols=1000, default=0)
    positions = [(0, 0), (0, 999), (500, 500), (999, 0), (999, 999),
                 (123, 456), (789, 12), (1, 998), (997, 3), (400, 600)]
    for i, (r, c) in enumerate(positions):
        m.set(r, c, i + 1)
    assert_equal(len(m), 10, "test_large_sparse: entry count")
    assert_equal(m.get(500, 500), 3, "test_large_sparse: spot check")
    assert_equal(m.get(0, 1), 0,     "test_large_sparse: default cell")


# ==========================================================================
# multiply()
# ==========================================================================

def test_multiply_basic():
    """Hand-computed 2×2 example: [[1,2],[3,4]] * [[5,6],[7,8]] = [[19,22],[43,50]]."""
    a = SparseMatrix(rows=2, cols=2, default=0)
    a.set(0, 0, 1); a.set(0, 1, 2)
    a.set(1, 0, 3); a.set(1, 1, 4)

    b = SparseMatrix(rows=2, cols=2, default=0)
    b.set(0, 0, 5); b.set(0, 1, 6)
    b.set(1, 0, 7); b.set(1, 1, 8)

    c = a.multiply(b)
    assert_equal(c.get(0, 0), 19, "test_multiply_basic: (0,0)")
    assert_equal(c.get(0, 1), 22, "test_multiply_basic: (0,1)")
    assert_equal(c.get(1, 0), 43, "test_multiply_basic: (1,0)")
    assert_equal(c.get(1, 1), 50, "test_multiply_basic: (1,1)")


def test_multiply_identity():
    """A * I == A for a 2×2 matrix."""
    a = SparseMatrix(rows=2, cols=2, default=0)
    a.set(0, 0, 3); a.set(0, 1, 7)
    a.set(1, 0, 2); a.set(1, 1, 5)

    I = SparseMatrix(rows=2, cols=2, default=0)
    I.set(0, 0, 1); I.set(1, 1, 1)

    c = a.multiply(I)
    assert_equal(c.get(0, 0), 3, "test_multiply_identity: (0,0)")
    assert_equal(c.get(0, 1), 7, "test_multiply_identity: (0,1)")
    assert_equal(c.get(1, 0), 2, "test_multiply_identity: (1,0)")
    assert_equal(c.get(1, 1), 5, "test_multiply_identity: (1,1)")


def test_multiply_zero():
    """A * zero-matrix should give all zeros (empty result)."""
    a = SparseMatrix(rows=2, cols=2, default=0)
    a.set(0, 0, 5); a.set(1, 1, 3)

    z = SparseMatrix(rows=2, cols=2, default=0)  # no entries set

    c = a.multiply(z)
    assert_equal(c.get(0, 0), 0, "test_multiply_zero: (0,0)")
    assert_equal(c.get(0, 1), 0, "test_multiply_zero: (0,1)")
    assert_equal(c.get(1, 0), 0, "test_multiply_zero: (1,0)")
    assert_equal(c.get(1, 1), 0, "test_multiply_zero: (1,1)")
    assert_equal(len(c), 0,      "test_multiply_zero: len should be 0")


def test_multiply_incompatible_dimensions():
    """multiply() should raise ValueError when dimensions are incompatible."""
    a = SparseMatrix(rows=2, cols=3, default=0)
    b = SparseMatrix(rows=2, cols=2, default=0)
    try:
        a.multiply(b)
        raise AssertionError("test_multiply_incompatible_dimensions: expected ValueError")
    except ValueError:
        pass  # correct


def test_multiply_non_square():
    """2×3 multiplied by 3×2 should yield a 2×2 result."""
    # A = [[1,0,2],[0,3,0]]  B = [[1,0],[0,1],[2,0]]
    # A*B = [[5,0],[0,3]]
    a = SparseMatrix(rows=2, cols=3, default=0)
    a.set(0, 0, 1); a.set(0, 2, 2); a.set(1, 1, 3)

    b = SparseMatrix(rows=3, cols=2, default=0)
    b.set(0, 0, 1); b.set(1, 1, 1); b.set(2, 0, 2)

    c = a.multiply(b)
    assert_equal(c.get(0, 0), 5, "test_multiply_non_square: (0,0)")
    assert_equal(c.get(0, 1), 0, "test_multiply_non_square: (0,1)")
    assert_equal(c.get(1, 0), 0, "test_multiply_non_square: (1,0)")
    assert_equal(c.get(1, 1), 3, "test_multiply_non_square: (1,1)")


# ==========================================================================
# __str__
# ==========================================================================

def test_str_non_empty():
    """__str__ should return a non-empty string."""
    m = SparseMatrix(rows=2, cols=2, default=0)
    m.set(0, 0, 1)
    result = str(m)
    assert isinstance(result, str) and len(result) > 0, \
        f"test_str_non_empty: got {result!r}"


def test_str_contains_values():
    """__str__ output should contain the values that were set."""
    m = SparseMatrix(rows=2, cols=2, default=0)
    m.set(0, 0, 7)
    m.set(1, 1, 3)
    result = str(m)
    assert "7" in result, f"test_str_contains_values: '7' missing from {result!r}"
    assert "3" in result, f"test_str_contains_values: '3' missing from {result!r}"


# ==========================================================================
# Runner
# ==========================================================================

if __name__ == '__main__':
    tests = [
        test_set_and_get,
        test_default_value,
        test_custom_default,
        test_overwrite,
        test_set_to_default_removes_entry,
        test_len_empty,
        test_len_after_set,
        test_items_empty,
        test_items_yields_correct_entries,
        test_items_consistent_with_get,
        test_large_sparse,
        test_multiply_basic,
        test_multiply_identity,
        test_multiply_zero,
        test_multiply_incompatible_dimensions,
        test_multiply_non_square,
        test_str_non_empty,
        test_str_contains_values,
    ]

    passed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {test.__name__}: {e}")

    print(f"\n{passed}/{len(tests)} tests passed.")