"""
graph_tests.py - Unit tests for Graph

Author: [Your Name]
Date:   [Date]
Lab:    Lab 7 - NPC Dialog with Graphs

TODO (Part 5)
-------------
Write at least ten tests. Your tests must cover all of these:
  - add_node, add_edge, has_node, has_edge
  - get_neighbors, get_node_data
  - remove_node, remove_edge
  - bfs  (check discovery order and reachability)
  - dfs  (check discovery order and reachability)
  - shortest_path (path exists, no path exists, self-path)
  - directed vs. undirected edge semantics
  - edge cases: disconnected graph, isolated node, self-loop

Run with:
    cd code/game/datastructures/tests
    python graph_tests.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.graph import Graph


# ---------------------------------------------------------------------------
# TODO: Write at least 10 tests below.
# Each function must start with 'test_', use assert, and print "PASS <name>".
# Below are some examples you could implement.
# ---------------------------------------------------------------------------
def test_add_and_has_node_edge():
    """Verify adding nodes and edges, and checking their existence."""
    g = Graph(directed=True)
    g.add_node("A", data="First Node")
    g.add_node("B")
    g.add_edge("A", "B", weight=5, edge_data="Link")
    
    assert g.has_node("A") is True
    assert g.has_node("C") is False
    # Check edge existence via neighbors
    neighbors = [n for n, w, d in g.get_neighbors("A")]
    assert "B" in neighbors
    print("PASS test_add_and_has_node_edge")

def test_get_node_data_and_neighbors():
    """Verify retrieval of node data and neighbor information."""
    g = Graph()
    g.add_node("A", data={"text": "Hello"})
    g.add_node("B")
    g.add_edge("A", "B", edge_data="Choice 1")
    
    assert g.get_node_data("A") == {"text": "Hello"}
    neighbors = g.get_neighbors("A")
    assert len(neighbors) == 1
    assert neighbors[0][2] == "Choice 1" # Verify edge_data
    print("PASS test_get_node_data_and_neighbors")

def test_remove_node_and_edge():
    """Test deletion of edges and nodes, ensuring edges are cleaned up."""
    g = Graph(directed=True)
    g.add_node("A")
    g.add_node("B")
    g.add_edge("A", "B")
    
    g.remove_edge("A", "B")
    assert len(g.get_neighbors("A")) == 0
    
    g.add_edge("A", "B")
    g.remove_node("B")
    assert g.has_node("B") is False
    # Edges connected to the deleted node should also be removed
    assert len(g.get_neighbors("A")) == 0
    print("PASS test_remove_node_and_edge")

def test_directed_vs_undirected():
    """Compare behavior between directed and undirected graph instances."""
    # Directed Graph Test
    dg = Graph(directed=True)
    dg.add_edge("A", "B")
    assert "B" in [n for n, w, d in dg.get_neighbors("A")]
    assert "A" not in [n for n, w, d in dg.get_neighbors("B")]
    
    # Undirected Graph Test
    ug = Graph(directed=False)
    ug.add_edge("A", "B")
    assert "B" in [n for n, w, d in ug.get_neighbors("A")]
    assert "A" in [n for n, w, d in ug.get_neighbors("B")]
    print("PASS test_directed_vs_undirected")

def test_bfs_order():
    """Check if BFS visits nodes in the correct layer-by-layer order."""
    g = Graph(directed=True)
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")
    
    order = g.bfs("A")
    # BFS should follow A -> (B, C in any order) -> D
    assert order[0] == "A"
    assert set(order[1:3]) == {"B", "C"}
    assert order[3] == "D"
    print("PASS test_bfs_order")

def test_dfs_order():
    """Verify DFS traversal order."""
    g = Graph(directed=True)
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    
    order = g.dfs("A")
    # DFS should follow the path A -> B -> C
    assert order == ["A", "B", "C"]
    print("PASS test_dfs_order")

def test_shortest_path_exists():
    """Ensure the shortest path is correctly identified between nodes."""
    g = Graph(directed=False)
    g.add_edge("A", "B", weight=1)
    g.add_edge("B", "C", weight=1)
    g.add_edge("A", "C", weight=5)
    
    path = g.shortest_path("A", "C")
    # If using edge weights, ["A", "B", "C"] is shorter (2 vs 5)
    # If unweighted, ["A", "C"] might be returned by BFS.
    assert "A" in path and "C" in path
    print("PASS test_shortest_path_exists")

def test_shortest_path_not_found():
    """Test pathfinding between disconnected components."""
    g = Graph()
    g.add_node("A")
    g.add_node("Z")
    
    path = g.shortest_path("A", "Z")
    assert path is None or path == []
    print("PASS test_shortest_path_not_found")

def test_self_loop_and_isolated():
    """Check edge cases: nodes with self-loops and nodes with no edges."""
    g = Graph()
    g.add_node("Isolated")
    g.add_node("Loop")
    g.add_edge("Loop", "Loop") # Self-loop
    
    assert len(g.get_neighbors("Isolated")) == 0
    assert "Loop" in [n for n, w, d in g.get_neighbors("Loop")]
    print("PASS test_self_loop_and_isolated")

def test_shortest_path_self():
    """Verify that the shortest path from a node to itself is just the node."""
    g = Graph()
    g.add_node("A")
    path = g.shortest_path("A", "A")
    assert path == ["A"]
    print("PASS test_shortest_path_self")


# ---------------------------------------------------------------------------
# Do not modify
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        (name, fn)
        for name, fn in sorted(globals().items())
        if name.startswith("test_") and callable(fn)
    ]

    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
        except Exception as exc:
            print(f"FAIL {name}: {exc}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed / {passed + failed} total")
    if failed:
        sys.exit(1)
    else:
        print("All tests passed!")
